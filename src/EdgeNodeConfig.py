import os
import json
    
class EdgeNodeConfig:
    _instance = None
    config_path = "edgeNodeConfig.json"
    default_config = {
        "trustEngineUrl": "https://127.0.0.1:5001",
        "backendServerUrl": "https://127.0.0.1:5002",
        "secretKey": "PUT_YOUR_SECRET_HERE",
    }

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(EdgeNodeConfig, cls).__new__(cls)
            cls.instance._load_config()
        return cls.instance

    def _load_config(self):
        if not os.path.exists(self.config_path):
            with open(self.config_path, 'w') as f:
                json.dump(self.default_config, f, indent=4)
        with open(self.config_path) as f:
            self.config = json.load(f)

    def __getattr__(self, name):
        if name in self.config:
            return self.config[name]
        elif name in self.default_config:
            return self.default_config[name]
        else:
            raise AttributeError(f"'EdgeNodeConfig' object has no attribute '{name}'")

    def setValue(self, key, value):
        self.config[key] = value
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)
        