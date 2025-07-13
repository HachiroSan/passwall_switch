import os
import json

class Config:
    """Configuration manager for SSH credentials and app settings."""
    
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.default_config = {
            "ssh": {
                "host": "192.168.1.1",
                "user": "root",
                "port": 22,
                "password": None,
                "key_file": None
            },
            "app": {
                "poll_interval": 3,
                "theme": "dark_teal.xml"
            }
        }
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file or create default if not exists."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return {**self.default_config, **config}
            except Exception as e:
                print(f"Error loading config: {e}")
                return self.default_config
        else:
            self.save_config(self.default_config)
            return self.default_config
    
    def save_config(self, config=None):
        """Save configuration to file."""
        if config is None:
            config = self.config
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key_path):
        """Get configuration value using dot notation (e.g., 'ssh.host')."""
        keys = key_path.split('.')
        value = self.config
        for key in keys:
            value = value.get(key)
            if value is None:
                return None
        return value
    
    def set(self, key_path, value):
        """Set configuration value using dot notation and save."""
        keys = key_path.split('.')
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
        self.save_config() 