"""
Module: Network Investigator
Purpose: Runs diagnostic commands and parses output for potential issues.
"""
from connection import DeviceManager
from rich.console import Console
from rich.table import Table

console = Console()

class NetworkInvestigator:
    """
    Diagnoses network health by running specific commands and parsing for errors.
    """
    def __init__(self, device_dict):
        self.device = device_dict
        self.manager = DeviceManager(device_dict)

    def run_health_check(self):
        """
        Connects to the device and runs a suite of diagnostic commands.
        Returns a list of 'Issues Found'.
        """
        issues = []
        if not self.manager.connect():
            return ["❌ Critical: Device Unreachable"]

        # 1. Check Interface Status
        # We look for interfaces that should be up but are down
        print(f"🔎 Investigating {self.device['host']} interfaces...")
        int_output = self.manager.send_command("show ip interface brief")
        
        if int_output:
            for line in int_output.splitlines():
                # Simple logic: If an admin set it 'up', protocol should be 'up'
                if "up" in line and "down" in line:
                    # Parse the interface name (usually the first word)
                    int_name = line.split()[0]
                    issues.append(f"⚠️ Interface {int_name} is DOWN (Protocol mismatch)")

        # 2. Check for High CPU (Basic check)
        # Note: This is platform specific, assuming Cisco IOS behavior
        print(f"🔎 Checking CPU levels...")
        cpu_output = self.manager.send_command("show processes cpu sorted | exclude 0.00")
        if cpu_output:
            # Get the first line of CPU stats
            try:
                first_line = cpu_output.splitlines()[0]
                if "CPU utilization" in first_line:
                    # Extract the 5-minute average (last number usually)
                    # Example: "CPU utilization for five seconds: 1%/0%; one minute: 1%; five minutes: 1%"
                    if "five minutes" in first_line:
                        parts = first_line.split("five minutes: ")
                        if len(parts) > 1:
                            load = parts[1].replace("%", "").strip()
                            if int(load) > 80:
                                issues.append(f"🔥 High CPU Load: {load}% (5 min avg)")
            except Exception:
                pass # logic parsing error, skip

        self.manager.disconnect()
        return issues