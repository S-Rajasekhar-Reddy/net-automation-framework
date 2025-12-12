"""
Main execution script for the Network Automation Framework.
Handles both Operational tasks (Backups) and Engineering tasks (Config Generation).
"""
import os
import sys
import yaml
from rich.console import Console
from rich.table import Table
# We need to add the current directory to sys.path to find modules if needed
sys.path.append(os.getcwd())

from connection import DeviceManager
from modules.config_generator import ConfigGenerator
from modules.investigator import NetworkInvestigator

# Initialize pretty printing
console = Console()

def load_inventory(file_path):
    """Loads the YAML inventory file."""
    if not os.path.exists(file_path):
        console.print(f"[bold red]Error: Inventory file '{file_path}' not found![/bold red]")
        return []

    with open(file_path, 'r', encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get('all_devices', [])

def task_network_backup():
    """Executes the connectivity check and backup workflow."""
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

def task_config_generator():
    """Executes the IaC Config Generator workflow."""
    console.print("[bold blue]--- Configuration Generator ---[/bold blue]")
    
    # In a real app, we might scan the data/ folder. 
    # For now, we ask for the specific device name.
    target_device = input("Enter the target device name (e.g., switch_01): ")
    data_file = f"data/host_vars/{target_device}.yml"
    
    # Check if data exists
    if not os.path.exists(data_file):
        console.print(f"[bold red]❌ Error: Data file '{data_file}' not found![/bold red]")
        return

    # Initialize Generator
    generator = ConfigGenerator(template_dir="templates")
    template_name = "switch_template.j2" # Default for now
    
    # Generate
    output = generator.generate_config(template_name, data_file)
    
    if output:
        console.print(f"\n[green]✅ Configuration Generated Successfully for {target_device}:[/green]")
        print("-" * 40)
        print(output)
        print("-" * 40)
        
        # Optional: Save to file
        save_choice = input("Do you want to save this to a file? (y/n): ")
        if save_choice.lower() == 'y':
            with open(f"{target_device}.cfg", "w", encoding="utf-8") as f:
                f.write(output)
            console.print(f"💾 Saved to {target_device}.cfg")

def task_investigator():
    """Executes the Network Investigator workflow."""
    inventory_file = 'inventory/devices.yml'
    devices = load_inventory(inventory_file)
    
    if not devices:
        console.print("[yellow]No devices found.[/yellow]")
        return

    console.print("[bold purple]--- Network Investigator (Health Check) ---[/bold purple]")
    
    # Create a results table
    table = Table(title="Network Health Report")
    table.add_column("Device", style="cyan")
    table.add_column("Health Status", style="green")
    table.add_column("Issues Found", style="red")

    for device in devices:
        investigator = NetworkInvestigator(device)
        issues = investigator.run_health_check()
        
        if not issues:
            table.add_row(device['host'], "✅ Healthy", "None")
        elif "Device Unreachable" in issues[0]:
            table.add_row(device['host'], "❌ Unreachable", "Connection Failed")
        else:
            # Join multiple issues with a newline for the table
            formatted_issues = "\n".join(issues)
            table.add_row(device['host'], "⚠️ Attention Needed", formatted_issues)

    console.print(table)

def main():
    """Main Menu Entry Point."""
    console.print("[bold yellow]Network Automation Framework[/bold yellow]")
    console.print("1. 📡 Run Network Connectivity & Backup")
    console.print("2. ⚙️ Generate Device Configuration (IaC)")
    console.print("3. 🕵️ Run Network Investigator (Health Check)") # <-- New Option
    console.print("4. 🚪 Exit")
    
    choice = input("\nSelect an option (1-4): ")
    
    if choice == '1':
        task_network_backup()
    elif choice == '2':
        task_config_generator()
    elif choice == '3':
        task_investigator()
    elif choice == '4':
        console.print("Exiting...")
        sys.exit()
    else:
        console.print("[red]Invalid selection.[/red]")

if __name__ == "__main__":
    main()