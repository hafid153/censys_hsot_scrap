import yaml
import os

class InlineDict(dict):
    pass

def represent_inline_dict(dumper, data):
    return dumper.represent_mapping('tag:yaml.org,2002:map', data, flow_style=True)


yaml.add_representer(InlineDict, represent_inline_dict)


folder_path = "data_yml"  


merged_hosts = []


for filename in os.listdir(folder_path):
    if filename.endswith(".yaml") or filename.endswith(".yml"):
        path = os.path.join(folder_path, filename)
        with open(path, 'r', encoding='utf-8') as f:
            try:
                data = yaml.safe_load(f)
                if data and isinstance(data, dict):
                    
                    if 'ports' in data and isinstance(data['ports'], list):
                        data['ports'] = [InlineDict(p) for p in data['ports']]
                    merged_hosts.append(data)
            except yaml.YAMLError as e:
                print(f"[❌] Erreur dans {filename}: {e}")


final_output = {
    "hosts": merged_hosts
}


with open("data_yml/merged_hosts.yaml", 'w', encoding='utf-8') as out:
    yaml.dump(final_output, out, sort_keys=False, allow_unicode=True)

print(f"[✅] Fusion terminée. {len(merged_hosts)} fichiers → merged_hosts.yaml")
