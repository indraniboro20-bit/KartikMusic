import json
import os

locales_dir = 'KartikMusic/locales'
en_path = os.path.join(locales_dir, 'en.json')

with open(en_path, 'r', encoding='utf-8') as f:
    en_data = json.load(f)

for filename in os.listdir(locales_dir):
    if filename.endswith('.json') and filename != 'en.json':
        filepath = os.path.join(locales_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                continue

        missing_keys = set(en_data.keys()) - set(data.keys())
        if missing_keys:
            print(f"Updating {filename} with {len(missing_keys)} missing keys.")
            for key in missing_keys:
                if filename == 'hi.json' and key == 'add_mee':
                    data[key] = "मुझे जोड़ें"
                else:
                    data[key] = en_data[key]

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
