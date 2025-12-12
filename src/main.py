"""
Main execution script for the Network Automation Framework.
Integrates Operational (Backup), Engineering (IaC), Troubleshooting (Investigator), 
and Validation (Guardian) modules.
"""
import sys
import os
import yaml
import time
from rich.console import Console
from rich.table import Table

# Add current path to sys.path to ensure modules are found
sys.path.append(os.getcwd())

from connection import DeviceManager
from modules.config_generator import ConfigGenerator
from modules.investigator import NetworkInvestigator
from modules.validator import StateValidator

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

# --- TASK 1: OPS (Backup) ---
def task_network_backup():
    inventory_file = 'inventory/devices.yml'
    devices = load_inventory(inventory_file)
    if not devices: return

    table = Table(title="Network Device Backup Status")
    table.add_column("Device", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Outcome", style="green")

    for device in devices:
        manager = DeviceManager(device)
        if manager.connect():
            backup_path = manager.backup()
            status = f"💾 Saved: {os.path.basename(backup_path)}" if backup_path else "❌ Failed"
            table.add_row(device['host'], "✅ Online", status)
            manager.disconnect()
        else:
            table.add_row(device['host'], "❌ Offline", "N/A")
    console.print(table)

# --- TASK 2: DEV (Config Gen) ---
def task_config_generator():
    console.print("[bold blue]--- Configuration Generator ---[/bold blue]")
    target_device = input("Enter target device name (e.g., switch_01): ")
    data_file = f"data/host_vars/{target_device}.yml"
    
    if not os.path.exists(data_file):
        console.print(f"[red]Error: {data_file} not found.[/red]")
        return

    generator = ConfigGenerator(template_dir="templates")
    # Defaulting to switch_template for demo purposes
    output = generator.generate_config("switch_template.j2", data_file)
    
    if output:
        console.print(f"\n[green]✅ Generated Config for {target_device}:[/green]")
        print("-" * 40)
        print(output)
        print("-" * 40)

# --- TASK 3: INTEL (Investigator) ---
def task_investigator():
    inventory_file = 'inventory/devices.yml'
    devices = load_inventory(inventory_file)
    if not devices: return

    table = Table(title="Network Health Report")
    table.add_column("Device", style="cyan")
    table.add_column("Health", style="green")
    table.add_column("Issues", style="red")

    for device in devices:
        investigator = NetworkInvestigator(device)
        issues = investigator.run_health_check()
        
        if not issues:
            table.add_row(device['host'], "✅ Healthy", "None")
        elif "Unreachable" in issues[0]:
            table.add_row(device['host'], "❌ Unreachable", "Connection Failed")
        else:
            table.add_row(device['host'], "⚠️ Issues", "\n".join(issues))
    console.print(table)

# --- TASK 4: GUARDIAN (State Validator) ---
def task_guardian():
    console.print("[bold purple]--- Guardian State Validator ---[/bold purple]")
    inventory_file = 'inventory/devices.yml'
    devices = load_inventory(inventory_file)
    
    # Simple selection for demo: Pick the first device or ask user
    if not devices: return
    target = devices[0] # Default to first device for simplicity
    console.print(f"🛡️ Guarding Target: [cyan]{target['host']}[/cyan]")
    
    manager = DeviceManager(target)
    validator = StateValidator()
    
    # 1. Take Pre-Change Snapshot
    if not manager.connect(): return
    console.print("📸 Taking PRE-CHANGE snapshot...")
    # For Linux test, we use 'ip a' or 'uname -a'. For Cisco, 'show ip route'.
    cmd = "show ip route" if target['device_type'] == 'cisco_ios' else "ip address"
    
    pre_content = manager.get_state(cmd)
    pre_file = validator.save_snapshot(target['host'], pre_content, "PRE")
    console.print(f"✅ Saved: {pre_file}")
    
    # 2. Pause for User Action
    console.print("\n[yellow]⏸️  PAUSED: Make your changes on the device now.[/yellow]")
    input("Press Enter once changes are complete...")
    
    # 3. Take Post-Change Snapshot
    console.print("📸 Taking POST-CHANGE snapshot...")
    post_content = manager.get_state(cmd)
    post_file = validator.save_snapshot(target['host'], post_content, "POST")
    console.print(f"✅ Saved: {post_file}")
    manager.disconnect()
    
    # 4. Compare
    console.print("\n🔍 Comparing States...")
    diff_report = validator.compare_files(pre_file, post_file)
    print("-" * 40)
    print(diff_report)
    print("-" * 40)

def main():
    while True:
        console.print("\n[bold yellow]Network Automation Framework[/bold yellow]")
        console.print("1. 📡 Run Network Backup (Ops)")
        console.print("2. ⚙️ Generate Config (Dev)")
        console.print("3. 🕵️ Run Health Check (Intel)")
        console.print("4. 🛡️ Run State Validator (Guardian)")
        console.print("5. 🚪 Exit")
        
        choice = input("\nSelect option: ")
        
        if choice == '1': task_network_backup()
        elif choice == '2': task_config_generator()
        elif choice == '3': task_investigator()
        elif choice == '4': task_guardian()
        elif choice == '5': sys.exit()
        else: console.print("[red]Invalid selection[/red]")

if __name__ == "__main__":
    main()