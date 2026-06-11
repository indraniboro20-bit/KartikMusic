import json
import os

locales_dir = 'KartikMusic/locales'
en_path = os.path.join(locales_dir, 'en.json')

with open(en_path, 'r') as f:
    en_data = json.load(f)

en_keys = set(en_data.keys())

for filename in os.listdir(locales_dir):
    if filename.endswith('.json') and filename != 'en.json':
        filepath = os.path.join(locales_dir, filename)
        with open(filepath, 'r') as f:
            try:
                data = json.load(f)
                missing = en_keys - set(data.keys())
                if missing:
                    print(f"{filename} is missing: {sorted(list(missing))}")
            except Exception as e:
                print(f"Error reading {filename}: {e}")
