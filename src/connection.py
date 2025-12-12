"""
Handles network device connectivity and interaction using Netmiko.
"""
import logging
# Pylint E0401: We rely on PYTHONPATH being set correctly in execution
from utils import save_to_file
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException

# Set up logging
logging.basicConfig(
    filename='logs/network_automation.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DeviceManager:
    """
    A class to handle the lifecycle of a network connection.
    Encapsulates Netmiko logic to make it reusable.
    """

    def __init__(self, device_dict):
        self.device_dict = device_dict
        self.connection = None

    def connect(self):
        """Establishes the SSH connection safely."""
        try:
            print(f"⏳ Connecting to {self.device_dict['host']}...")
            self.connection = ConnectHandler(**self.device_dict)
            # Pylint W1203: Use lazy % formatting
            logging.info("Success: Connected to %s", self.device_dict['host'])
            return True
        except (NetmikoTimeoutException, NetmikoAuthenticationException) as e:
            print(f"❌ Connection Failed: {e}")
            logging.error("Failed to connect to %s: %s", self.device_dict['host'], e)
            return False
        # pylint: disable=broad-exception-caught
        except Exception as e:
            print(f"❌ Unknown Error: {e}")
            logging.error("Unknown error for %s: %s", self.device_dict['host'], e)
            return False

    def send_command(self, command):
        """Sends a CLI command and returns the string output."""
        if not self.connection:
            return None
        try:
            output = self.connection.send_command(command)
            logging.info("Command '%s' sent to %s", command, self.device_dict['host'])
            return output
        # pylint: disable=broad-exception-caught
        except Exception as e:
            logging.error("Command execution failed: %s", e)
            return None

    def backup(self):
        """Retrieves the running configuration and saves it to a file."""
        if not self.connection:
            return False

        try:
            CMD_MAP = {
                "cisco_ios": "show running-config",
                "cisco_xr": "show running-config",
                "juniper_junos": "show configuration",
                "arista_eos": "show running-config",
                "linux": "cat /etc/os-release"  # For our test lab
            }
        
            # Get the command based on device_type (default to cisco_ios if unknown)
            device_type = self.device_dict.get('device_type', 'cisco_ios')
            command = CMD_MAP.get(device_type, "show running-config")
    
            print(f"💾 Backing up {self.device_dict['host']} using '{command}'...")
    
            config_output = self.send_command(command)

            if not config_output or "denied" in config_output.lower():
                logging.error("Command returned empty/denied on %s", self.device_dict['host'])
                return False

            saved_path = save_to_file(self.device_dict['host'], config_output)
            logging.info("Backup saved to %s", saved_path)
            return saved_path

        # pylint: disable=broad-exception-caught
        except Exception as e:
            logging.error("Backup failed: %s", e)
            return False
    
    def get_state(self, command="show ip route"):
        """Runs a command to capture state (default: routing table)."""
        if not self.connection:
            return None
        print(f"📸 Capturing state for {self.device_dict['host']}...")
        return self.send_command(command)

    def disconnect(self):
        """Closes the SSH session."""
        if self.connection:
            self.connection.disconnect()
            logging.info("Disconnected from %s", self.device_dict['host'])