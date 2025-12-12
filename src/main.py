"""
Main execution script for the Network Automation Framework.
"""
import os
import yaml
from rich.console import Console
from rich.table import Table
# Pylint E0401: We rely on PYTHONPATH being set correctly in execution
from connection import DeviceManager

# Initialize pretty printing
console = Console()

def load_inventory(file_path):
    """Loads the YAML inventory file."""
    if not os.path.exists(file_path):
        console.print(f"[bold red]Error: Inventory file '{file_path}' not found![/bold red]")
        return []

    # Pylint W1514: Specify encoding
    with open(file_path, 'r', encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get('all_devices', [])

def main():
    """Main runner function."""
    inventory_file = 'inventory/devices.yml'
    devices = load_inventory(inventory_file)

    if not devices:
        console.print("[yellow]No devices found in inventory.[/yellow]")
        return

    table = Table(title="Network Device Backup Status")
    table.add_column("Device", style="cyan")
    table.add_column("Connection", style="magenta")
    table.add_column("Backup Status", style="green")

    for device in devices:
        manager = DeviceManager(device)

        if manager.connect():
            backup_path = manager.backup()

            if backup_path:
                filename = os.path.basename(backup_path)
                table.add_row(device['host'], "✅ Online", f"💾 Saved: {filename}")
            else:
                table.add_row(device['host'], "✅ Online", "❌ Backup Failed")

            manager.disconnect()
        else:
            table.add_row(device['host'], "❌ Offline", "N/A")

    console.print(table)

if __name__ == "__main__":
    main()