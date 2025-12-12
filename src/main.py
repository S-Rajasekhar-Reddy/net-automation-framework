import yaml
from rich.console import Console
from rich.table import Table
from connection import DeviceManager

# Initialize pretty printing
console = Console()

def load_inventory(file_path):
    """Loads the YAML inventory file."""
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)
    return data.get('all_devices', [])

def main():
    # 1. Load Data
    inventory_file = 'inventory/devices.yml'
    devices = load_inventory(inventory_file)

    # 2. Prepare the Table
    table = Table(title="Network Device Connectivity Check")
    table.add_column("Device", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Version", style="green")

    # 3. Iterate through devices (The Automation Loop)
    for device in devices:
        manager = DeviceManager(device)
        
        if manager.connect():
            # Get the version to prove we are actually logged in
            output = manager.send_command("uname -a")
            short_version = output.splitlines()[0] if output else "Unknown"
            
            table.add_row(device['host'], "✅ Online", short_version)
            manager.disconnect()
        else:
            table.add_row(device['host'], "❌ Offline", "N/A")

    console.print(table)

if __name__ == "__main__":
    main()