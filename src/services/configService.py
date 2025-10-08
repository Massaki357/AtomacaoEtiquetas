import json

class ConfigService:
    def __init__(self, filepath='config-program.json'):
        self.filepath = filepath

    def load_config(self):
        with open(self.filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_config(self, config):
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)