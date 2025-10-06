# censys_hsot_scrap



## Prerequisites

- [Node.js](https://nodejs.org/) (version v18.19.0 or higher)  
- Python 3.6+  
- `pip` for Python package management  

---

## Installation & Setup

1. **Prepare URL file**  
   Create a file named `url.txt` in the project root and add the target URL inside.

2. **Install Node.js dependencies**  
   ```bash
   cd node_js/
   npm install
   cd ..

3. **Create and activate Python virtual environment**
    '''bash
    python -m venv project-env
    source project-env/bin/activate

4. **Install Python dependencies**
   '''bash
   pip install -r requirements.txt

## Usage 
   '''bash
   python main.py
   
# Result 
	The script will generate a hosts.yml file containing the hosts and thiers port : serivce 

