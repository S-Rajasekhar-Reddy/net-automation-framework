import logging
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException

# This creates a file that tracks what your script did
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
            logging.info(f"Success: Connected to {self.device_dict['host']}")
            return True
        except (NetmikoTimeoutException, NetmikoAuthenticationException) as e:
            print(f"❌ Connection Failed: {e}")
            logging.error(f"Failed to connect to {self.device_dict['host']}: {e}")
            return False
        except Exception as e:
            print(f"❌ Unknown Error: {e}")
            logging.error(f"Unknown error for {self.device_dict['host']}: {e}")
            return False

    def send_command(self, command):
        """Sends a CLI command and returns the string output."""
        if not self.connection:
            return None
        try:
            output = self.connection.send_command(command)
            logging.info(f"Command '{command}' sent to {self.device_dict['host']}")
            return output
        except Exception as e:
            logging.error(f"Command execution failed: {e}")
            return None

    def disconnect(self):
        """Closes the SSH session."""
        if self.connection:
            self.connection.disconnect()
            logging.info(f"Disconnected from {self.device_dict['host']}")