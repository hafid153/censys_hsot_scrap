# main.py
import subprocess
import sys
import os
from data_processor import run_data_process

URL_FILE = 'url.txt'
PAGE_TEXT = os.path.join('node_js', 'page_text.txt')

def read_url():
    if not os.path.exists(URL_FILE):
        print(f"Erreur: {URL_FILE} introuvable.")
        sys.exit(1)
    with open(URL_FILE, 'r', encoding='utf-8') as f:
        url = f.read().strip()
    if not url:
        print("Erreur: url.txt est vide.")
        sys.exit(1)
    return url

def run_indexjs(url):
    cmd = ['node', 'node_js/index.js', url]
    print(f"▶ Lancement de index.js pour : {url}")
    # Ne pas capturer stdout/stderr : on veut que les messages de progression s'affichent dans le terminal.
    result = subprocess.run(cmd)
    # result.returncode contient le code de sortie ; on ne sort pas automatiquement pour permettre la collecte du fichier page_text.txt
    if result.returncode != 0:
        print(f"index.js s'est terminé avec le code {result.returncode} (voir logs ci‑dessous).")
    return result.returncode

def read_page_text():
    if not os.path.exists(PAGE_TEXT):
        print(f"Erreur: {PAGE_TEXT} introuvable. index.js n'a peut-être pas généré le fichier.")
        return None
    with open(PAGE_TEXT, 'r', encoding='utf-8') as f:
        return f.read()

def main():
    url = read_url()
    rc = run_indexjs(url)
    data = read_page_text()
    if data is None or not data.strip():
        print("Aucun texte extrait à traiter (page_text.txt vide ou manquant).")
        # si index.js a retourné une erreur, on renvoie cette erreur ; sinon on sort avec code 1
        sys.exit(rc if rc != 0 else 1)
    # On passe la chaîne de texte au parser Python
    run_data_process(data)
    # si tout s'est bien passé, on sort à 0
    sys.exit(0)

if __name__ == "__main__":
    main()
