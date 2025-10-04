import subprocess


with open('url.txt', 'r',encoding='utf-8') as file :
    url= str(file.read())

arg_for_index = url
arg1_for_data = "node_js/page_text.txt" 
arg2_for_data = "hosts.yml" 


def fetch_data(url,arg_for_index):
   
   # run index.js pour avoir le ficheir page_txt.txt
    result_node = subprocess.run(['node', 'node_js/index.js', arg_for_index])
    
    if result_node.returncode != 0:
        print("Erreur lors de l'exécution de index.js")
        exit(1)

def data_process(arg1_for_data,arg2_for_data):

    # run dataprocess pour les  mettre dans un ficheir .yaml
    result_py = subprocess.run(['python', 'data_processor.py', arg1_for_data, arg2_for_data])
    
    if result_py.returncode != 0:
        print("Erreur lors de l'exécution de data_processor.py")
        exit(1)
    
def main():

     fetch_data(url,arg_for_index)
     data_process(arg1_for_data,arg2_for_data)



if __name__ == "__main__":
    main()
   
