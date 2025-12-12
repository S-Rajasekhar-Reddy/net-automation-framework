"""
Module: Config Generator
Purpose: Combines YAML data with Jinja2 templates to generate network configurations.
"""
import os
import yaml
from jinja2 import Environment, FileSystemLoader

class ConfigGenerator:
    """
    Handles the loading of data and rendering of templates.
    """
    def __init__(self, template_dir="templates"):
        # Initialize Jinja2 Environment
        # trim_blocks=True removes extra newlines from the output
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def load_data(self, data_file):
        """Loads YAML data from a specific file."""
        if not os.path.exists(data_file):
            print(f"❌ Error: Data file '{data_file}' not found.")
            return None
        
        with open(data_file, 'r') as f:
            return yaml.safe_load(f)

    def generate_config(self, template_name, data_file):
        """Renders the template with the provided data."""
        # 1. Load the Data
        data = self.load_data(data_file)
        if not data:
            return None

        # 2. Load the Template
        try:
            template = self.env.get_template(template_name)
        except Exception as e:
            print(f"❌ Error loading template '{template_name}': {e}")
            return None

        # 3. Render (Combine Data + Template)
        try:
            print(f"⚙️ Generating config for {data.get('hostname', 'device')}...")
            config_output = template.render(data)
            return config_output
        except Exception as e:
            print(f"❌ Error rendering config: {e}")
            return None