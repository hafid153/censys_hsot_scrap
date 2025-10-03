import subprocess


with open('url.txt', 'r',encoding='utf-8') as file :
    url= str(file.read())


arg_for_index = url
arg1_for_data = "node_js/page_text.txt" # remplace par ton argument réel pour data_processor.py
arg2_for_data = "hosts.yml" # remplace par ton argument réel pour data_processor.py

# Lancer index.js avec son argument
result_node = subprocess.run(['node', 'node_js/index.js', arg_for_index])

if result_node.returncode != 0:
    print("Erreur lors de l'exécution de index.js")
    exit(1)

# Lancer data_processor.py avec ses arguments
result_py = subprocess.run(['python', 'data_processor.py', arg1_for_data, arg2_for_data])

if result_py.returncode != 0:
    print("Erreur lors de l'exécution de data_processor.py")
    exit(1)

print("Les deux scripts ont été exécutés avec succès.")
