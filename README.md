Here's the updated `README.md` with an added section on deploying a DarkSky CS training range:

---

# ProxMox-Template-Deployment (deploy_vms.py)

## Overview

`deploy_vms.py` is a Python script designed to automate the deployment of virtual machines (VMs) on a Proxmox server. This script allows you to:

- Deploy VMs from specified templates.
- Create or check the existence of a Virtual Network (VNet) and zone.
- Create or check the existence of a resource pool.
- Optionally power on the deployed VMs.
- Undo the deployment by removing VMs, VNet, and resource pool.

## Features

- **Deploy VMs**: Clone VMs from provided templates to new IDs.
- **Create Networks and Zones**: Automatically create a VNet and a zone if they do not exist.
- **Resource Pools**: Create or verify the existence of a resource pool.
- **Power On VMs**: Optionally power on the VMs after deployment.
- **Undo Changes**: Remove VMs, VNet, and resource pool if needed.
- **Debug Mode**: Provides detailed logs for troubleshooting.

## Requirements

- Python 3.x
- `proxmoxer` library (install via `pip install proxmoxer`)
- Access to a Proxmox server

## Usage

### Command-Line Arguments

- `--host`: Proxmox server address (e.g., `https://proxmox.example.com:8006`).
- `--user`: Proxmox user (default is `root@pam`).
- `--password`: Proxmox password (will prompt if not provided).
- `--vnet`: Name of the VNet to use or create.
- `--zone`: Name of the zone to use or create.
- `--resource_pool`: ID of the resource pool to use or create.
- `--starting_id`: Starting ID for the new VMs.
- `--templates`: List of VM template IDs to deploy.
- `--node_name`: Proxmox node name (default is `pve`).
- `--power_on`: Optionally power on the VMs after deployment.
- `--undo`: Undo changes by removing created VMs, VNet, and resource pool.
- `--debug`: Enable debug output.

### Example Commands

1. **Deploy VMs for DarkSky CS Training**

   To deploy VMs for a training environment using specific templates, with a new VNet, zone, and resource pool, and power them on:

   ```sh
   python3 deploy_vms.py --host 192.168.1.27 --user root@pam --vnet csvnet01 --zone cszone --templates 950 951 952 953 954 955 956 --starting_id 310 --resource_pool CSTraning01 --debug --power_on
   ```

   - **`--host 192.168.1.27`**: Specifies the Proxmox server address.
   - **`--user root@pam`**: Uses the `root@pam` user for authentication.
   - **`--vnet csvnet01`**: Use or create the VNet named `csvnet01`.
   - **`--zone cszone`**: Use or create the zone named `cszone`.
   - **`--templates 950 951 952 953 954 955 956`**: Deploy VMs from these templates.
   - **`--starting_id 310`**: Start VM IDs from 310.
   - **`--resource_pool CSTraning01`**: Use or create the resource pool named `CSTraning01`.
   - **`--debug`**: Enable debug output for detailed logs.
   - **`--power_on`**: Power on the VMs after deployment.

2. **Undo Deployment**

   To undo the deployment by removing VMs, VNet, and resource pool:

   ```sh
   python3 deploy_vms.py --host 192.168.1.27 --user root@pam --vnet csvnet01 --zone cszone --resource_pool CSTraning01 --starting_id 310 --templates 950 951 952 953 954 955 956 --undo
   ```

   - **`--undo`**: Removes the deployed VMs, VNet, and resource pool.

## How to Deploy a DarkSky CS Training Range

The DarkSky CS training range setup involves deploying multiple VMs from a series of templates, creating a specific VNet and zone, and setting up a resource pool for the training environment. Here's how to do it:

1. **Prepare Your Environment**
   - Ensure your Proxmox server is accessible and you have the necessary permissions.
   - Gather the VM template IDs that will be used for the training environment.

2. **Deploy VMs**
   - Use the command below to deploy the training VMs, create or use the specified VNet, zone, and resource pool, and optionally power them on:

   ```sh
   python3 deploy_vms.py --host 192.168.1.27 --user root@pam --vnet csvnet01 --zone cszone --templates 950 951 952 953 954 955 956 --starting_id 310 --resource_pool CSTraning01 --debug --power_on
   ```

   In this example:
   - **`--vnet csvnet01`**: Specifies the VNet for the VMs.
   - **`--zone cszone`**: Specifies the zone where the VNet will be created.
   - **`--templates 950 951 952 953 954 955 956`**: Specifies the VM templates to be deployed.
   - **`--starting_id 310`**: Sets the starting VM ID.
   - **`--resource_pool CSTraning01`**: Specifies the resource pool.
   - **`--power_on`**: Powers on the VMs after deployment.

3. **Check Deployment**
   - Verify the deployment in your Proxmox interface.
   - Ensure the VMs are running and configured correctly.

4. **Undo Changes (if needed)**
   - To remove all deployed VMs, VNet, and resource pool, use:

   ```sh
   python3 deploy_vms.py --host 192.168.1.27 --user root@pam --vnet csvnet01 --zone cszone --resource_pool CSTraning01 --starting_id 310 --templates 950 951 952 953 954 955 956 --undo
   ```

## Troubleshooting

- **Authentication Issues**: Ensure the Proxmox credentials are correct.
- **Network/Zone/Pool Creation**: Verify that the VNet, zone, and resource pool names are correct and do not conflict with existing names.
- **Debug Mode**: Use `--debug` to get detailed logs for troubleshooting.

## License

This script is provided "as is" without warranties or guarantees. Use it at your own risk.

---

This `README.md` provides a clear explanation of how to use the script, including an example of deploying a DarkSky CS training range and additional details for troubleshooting and usage.
