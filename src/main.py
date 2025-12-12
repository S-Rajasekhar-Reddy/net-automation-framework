import yaml
import os
from rich.console import Console
from rich.table import Table
from connection import DeviceManager

# Initialize pretty printing
console = Console()

def load_inventory(file_path):
    """Loads the YAML inventory file."""
    # Check if file exists first to avoid crashing
    if not os.path.exists(file_path):
        console.print(f"[bold red]Error: Inventory file '{file_path}' not found![/bold red]")
        return []
        
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)
    return data.get('all_devices', [])

def main():
    # 1. Load Data
    inventory_file = 'inventory/devices.yml'
    devices = load_inventory(inventory_file)

    if not devices:
        console.print("[yellow]No devices found in inventory.[/yellow]")
        return

    # 2. Prepare the Table
    # We changed the columns to reflect the Backup task
    table = Table(title="Network Device Backup Status")
    table.add_column("Device", style="cyan")
    table.add_column("Connection", style="magenta")
    table.add_column("Backup Status", style="green")

    # 3. Iterate through devices (The Automation Loop)
    for device in devices:
        manager = DeviceManager(device)
        
        # Try to connect
        if manager.connect():
            # Run the Backup
            backup_path = manager.backup()
            
            if backup_path:
                # We strip the full path to just show the filename in the table
                # This handles both Windows (\) and Linux (/) separators
                filename = os.path.basename(backup_path)
                table.add_row(device['host'], "✅ Online", f"💾 Saved: {filename}")
            else:
                table.add_row(device['host'], "✅ Online", "❌ Backup Failed")
            
            # Always disconnect cleanly
            manager.disconnect()
        else:
            # If connection failed entirely
            table.add_row(device['host'], "❌ Offline", "N/A")

    # Show results
    console.print(table)

if __name__ == "__main__":
    main()