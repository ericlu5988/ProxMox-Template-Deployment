import argparse
import getpass
import time
import warnings
from proxmoxer import ProxmoxAPI
from urllib3.exceptions import InsecureRequestWarning
from argparse import RawTextHelpFormatter

# Suppress InsecureRequestWarning
warnings.filterwarnings('ignore', category=InsecureRequestWarning)

def check_network_exists(proxmox, zone, vnet_name, debug=False):
    """Check if the VNet exists in the specified zone."""
    if debug:
        print(f"Checking if VNet {vnet_name} exists in zone {zone}...")
    vnets = proxmox.cluster.sdn.vnets.get()
    if debug:
        print(f"VNet data: {vnets}")

    exists = any(vnet['vnet'] == vnet_name and vnet['zone'] == zone for vnet in vnets)
    if exists:
        print(f"VNet {vnet_name} already exists in zone {zone}.")
    else:
        print(f"VNet {vnet_name} does not exist in zone {zone}.")
    return exists

def create_network(proxmox, zone, vnet_name):
    """Create a new VNet in the specified zone and apply SDN changes."""
    print(f"Creating VNet {vnet_name} in zone {zone}...")
    proxmox.cluster.sdn.vnets.create(vnet=vnet_name, type='vnet', zone=zone)
    proxmox.cluster.sdn.put()  # Apply SDN changes
    print(f"VNet {vnet_name} created successfully.")

def check_resource_pool_exists(proxmox, pool_id, debug=False):
    """Check if the specified resource pool exists."""
    if debug:
        print(f"Checking if resource pool {pool_id} exists...")
    try:
        pools = proxmox.pools.get()
        pool_ids = [pool['poolid'] for pool in pools]
        exists = pool_id in pool_ids
        if exists:
            print(f"Resource pool {pool_id} exists.")
        else:
            print(f"Resource pool {pool_id} does not exist.")
        return exists
    except Exception as e:
        print(f"Error checking resource pool existence: {e}")
        return False

def create_resource_pool(proxmox, pool_id):
    """Create a new resource pool."""
    print(f"Creating resource pool {pool_id}...")
    proxmox.pools.post(poolid=pool_id)
    print(f"Resource pool {pool_id} created successfully.")

def check_zone_exists(proxmox, zone_name, debug=False):
    """Check if the specified zone exists."""
    if debug:
        print(f"Checking if zone {zone_name} exists...")
    zones = proxmox.cluster.sdn.zones.get()
    if debug:
        print(f"Zone data: {zones}")

    exists = any(zone['zone'] == zone_name for zone in zones)
    if exists:
        print(f"Zone {zone_name} already exists.")
    else:
        print(f"Zone {zone_name} does not exist.")
    return exists

def create_zone(proxmox, zone_name):
    """Create a new zone with type 'simple'."""
    print(f"Creating zone {zone_name} with type 'simple'...")
    proxmox.cluster.sdn.zones.create(
        zone=zone_name,
        type='simple'
    )
    proxmox.cluster.sdn.put()  # Apply SDN changes
    print(f"Zone {zone_name} created successfully.")

def check_vms_in_use(proxmox, node_name, vm_ids, debug=False):
    """Check if the specified VM IDs are already in use."""
    if debug:
        print(f"Checking if VM IDs are in use on node {node_name}...")
    vms = proxmox.nodes(node_name).qemu.get()
    existing_vms = [vm['vmid'] for vm in vms]
    
    in_use = False
    for vm_id in vm_ids:
        if vm_id in existing_vms:
            print(f"Error: VM ID {vm_id} is already in use.")
            in_use = True
    if not in_use:
        print("All VM IDs are available.")
    return in_use

def get_template_name(proxmox, node_name, template_id):
    """Fetch the name of the template."""
    try:
        template_info = proxmox.nodes(node_name).qemu(template_id).config.get()
        return template_info.get('name', f"template-{template_id}")
    except Exception as e:
        print(f"Error fetching template name: {e}")
        return f"template-{template_id}"

def deploy_vm(proxmox, node_name, template_id, new_vm_id, resource_pool, vnet_name, power_on=False, debug=False):
    """Deploy a VM from the specified template."""
    if debug:
        print(f"Deploying VM from template {template_id} to VM ID {new_vm_id}...")
    try:
        template_name = get_template_name(proxmox, node_name, template_id)
        proxmox.nodes(node_name).qemu(template_id).clone.post(
            newid=new_vm_id,
            name=template_name,
            pool=resource_pool
        )
        print(f"VM {new_vm_id} deployed successfully with name '{template_name}'.")

        # Configure network device
        proxmox.nodes(node_name).qemu(new_vm_id).config.post(
            net0=f"bridge={vnet_name},model=virtio"
        )
        print(f"Network device 'net0' for VM {new_vm_id} configured to use {vnet_name}.")

        # Optionally power on the VM
        if power_on:
            time.sleep(1)  # Small delay before powering on
            proxmox.nodes(node_name).qemu(new_vm_id).status.start.post()
            print(f"VM {new_vm_id} powered on successfully.")
    except Exception as e:
        print(f"Error deploying VM: {e}")

def undo_changes(proxmox, node_name, vnet_name, pool_id, starting_id, num_vms):
    """Undo changes: remove VMs, VNet, and resource pool."""
    print("Undoing changes...")

    # Remove VMs
    for vm_id in range(starting_id, starting_id + num_vms):
        try:
            proxmox.nodes(node_name).qemu(vm_id).delete()
            print(f"VM {vm_id} removed.")
            time.sleep(1)  # Small delay between operations
        except Exception as e:
            print(f"Error removing VM {vm_id}: {e}")

    # Remove VNet
    try:
        proxmox.cluster.sdn.vnets.delete(vnet_name)
        proxmox.cluster.sdn.put()  # Apply SDN changes
        print(f"VNet {vnet_name} removed.")
        time.sleep(1)  # Small delay between operations
    except Exception as e:
        print(f"Error removing VNet {vnet_name}: {e}")

    # Remove Resource Pool
    try:
        proxmox.pools.delete(pool_id)
        print(f"Resource pool {pool_id} removed.")
        time.sleep(1)  # Small delay between operations
    except Exception as e:
        print(f"Error removing resource pool {pool_id}: {e}")

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Deploy or undo deployment of VMs on Proxmox with specified network and resource pool.\n"
            "This script allows you to deploy VMs from specified templates, create a new VNet, zone, and resource pool if needed, and optionally power on the VMs. "
            "It also provides an option to undo changes by removing the created VMs, VNet, and resource pool.\n\n"
            "Examples:\n"
            "1. Deploy VMs with a new VNet, zone, and resource pool:\n"
            "   python deploy_vms.py --host https://proxmox.example.com:8006 --vnet csvnet03 --zone cszone --templates 950 951 952 --starting_id 300 --resource_pool CS03 --node_name pve\n\n"
            "2. Deploy VMs and power them on:\n"
            "   python deploy_vms.py --host https://proxmox.example.com:8006 --vnet csvnet03 --zone cszone --templates 950 951 952 --starting_id 300 --resource_pool CS03 --node_name pve --power_on\n\n"
            "3. Undo the deployment (remove VMs, VNet, and resource pool):\n"
            "   python deploy_vms.py --host https://proxmox.example.com:8006 --vnet csvnet03 --zone cszone --resource_pool CS03 --starting_id 300 --templates 950 951 952 --undo\n\n"
            "4. Debug mode for verbose output:\n"
            "   python deploy_vms.py --host https://proxmox.example.com:8006 --vnet csvnet03 --zone cszone --templates 950 951 952 --starting_id 300 --resource_pool CS03 --node_name pve --debug"
        ),
        formatter_class=RawTextHelpFormatter
    )

    parser.add_argument('--host', required=True, help='Proxmox host address (e.g., https://proxmox.example.com:8006).')
    parser.add_argument('--user', default='root@pam', help='Proxmox user (default: root@pam).')
    parser.add_argument('--password', help='Proxmox password (will prompt if not provided).')
    parser.add_argument('--vnet', required=True, help='Name of the VNet to use.')
    parser.add_argument('--zone', required=True, help='Name of the zone to use.')
    parser.add_argument('--resource_pool', required=True, help='ID of the resource pool to use.')
    parser.add_argument('--starting_id', type=int, required=True, help='Starting ID for VMs.')
    parser.add_argument('--templates', nargs='+', type=int, required=True, help='Template IDs to deploy.')
    parser.add_argument('--node_name', default='pve', help='Proxmox node name (default: pve).')
    parser.add_argument('--power_on', action='store_true', help='Power on VMs after deployment.')
    parser.add_argument('--undo', action='store_true', help='Undo changes by removing created VMs, VNet, and resource pool.')
    parser.add_argument('--debug', action='store_true', help='Enable debug output.')

    args = parser.parse_args()

    # Prompt for password if not provided
    if not args.password:
        args.password = getpass.getpass("Proxmox password: ")

    # Connect to Proxmox
    proxmox = ProxmoxAPI(
        args.host,
        user=args.user,
        password=args.password,
        verify_ssl=False
    )

    # Check and create zone if needed
    if not check_zone_exists(proxmox, args.zone, args.debug):
        create_zone(proxmox, args.zone)

    # Check and create network if needed
    if not check_network_exists(proxmox, args.zone, args.vnet, args.debug):
        create_network(proxmox, args.zone, args.vnet)

    # Check and create resource pool if needed
    if not check_resource_pool_exists(proxmox, args.resource_pool, args.debug):
        create_resource_pool(proxmox, args.resource_pool)

    # Perform deployment or undo changes
    if args.undo:
        undo_changes(proxmox, args.node_name, args.vnet, args.resource_pool, args.starting_id, len(args.templates))
    else:
        if check_vms_in_use(proxmox, args.node_name, list(range(args.starting_id, args.starting_id + len(args.templates))), args.debug):
            print("One or more VM IDs are already in use. Aborting deployment.")
        else:
            for i, template_id in enumerate(args.templates):
                deploy_vm(
                    proxmox,
                    args.node_name,
                    template_id,
                    args.starting_id + i,
                    args.resource_pool,
                    args.vnet,
                    power_on=args.power_on,
                    debug=args.debug
                )

if __name__ == "__main__":
    main()

