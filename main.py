import subprocess
import sys
import os
from data_processor import run_data_process

URL_FILE = 'url.txt'
PAGES_TEXT_SCRAPED_DIR_PATH  = os.path.join('node_js','data')
EXTRACTED_HOST_YAML_DIR_PATH = os.path.join('data_yml')

if not os.path.exists(EXTRACTED_HOST_YAML_DIR_PATH):
    os.makedirs(EXTRACTED_HOST_YAML_DIR_PATH, exist_ok= True)

def read_url():
    if not os.path.exists(URL_FILE):
        print(f"Erreur : {URL_FILE} introuvable.")
        sys.exit(1)
    
    with open(URL_FILE, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()] 

    if not urls:
        print("Erreur : url.txt est vide ou ne contient que des lignes vides.")
        sys.exit(1)

    return urls

def run_indexjs(url,output_filename):
    cmd = ['node', 'node_js/index.js', url, output_filename]
    
    print(f"▶ Lancement de index.js ")
    result = subprocess.run(cmd)

    if result.returncode != 0:
        print(f"index.js s'est terminé avec le code {result.returncode} (voir logs ci‑dessous).")
    return result.returncode

def scraped_text_output_filename_manager(index):
    filename = f"text_visible_for_url{index+1}.txt"
    return filename

def yaml_file_extracted_manager(index):
    filename = f"hosts_for_url{index+1}.yaml"
    return filename


def read_page_text(file_path):
    if not os.path.exists(file_path):
        print(f"Erreur: {file_path} introuvable. index.js n'a peut-être pas généré le fichier.")
        return None
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def main():
    urls = read_url()

    for url in urls :
        index_url = urls.index(url)
        filename_txt = scraped_text_output_filename_manager(index_url)
        run_indexjs(url,filename_txt)
    
    files_page_scarped_list = os.listdir(PAGES_TEXT_SCRAPED_DIR_PATH)
    
    for file in files_page_scarped_list :
        file_path = os.path.join(PAGES_TEXT_SCRAPED_DIR_PATH, file)
        file_index = files_page_scarped_list.index(file)
        data = read_page_text(file_path)
        filename_yml = yaml_file_extracted_manager(file_index)
        filename_yml_path = os.path.join(EXTRACTED_HOST_YAML_DIR_PATH,filename_yml)
        run_data_process(data,filename_yml_path)






if __name__ == "__main__":
    main()
