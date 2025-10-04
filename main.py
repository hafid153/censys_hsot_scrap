import subprocess
from data_processor import run_data_process

with open('url.txt', 'r',encoding='utf-8') as file :
    url= str(file.read())

arg_for_index = url

def fetch_data(url,arg_for_index):
   
    result_node = subprocess.run(['node', 'node_js/index.js', arg_for_index])
    
    if result_node.returncode != 0:
        print("Erreur lors de l'exécution de index.js")
        exit(1)

def main():

     fetch_data(url,arg_for_index)
     run_data_process()



if __name__ == "__main__":
    main()
   
