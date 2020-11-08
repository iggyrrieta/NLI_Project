from flask import Flask, render_template, request # Web app
import os # to save/open files 
from datetime import datetime # to create folder with date

# ROOT FOLDER : Make things easier setting the root folder as the origin
import sys
root_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
sys.path.insert(0, root_path)
# DM
from dm_core.main import Core as dm_core

#############################################
# GLOBAL: CREATE LOCAL FOLDER WITH PERMISSION         
#############################################
now = datetime.now()
dt_string = now.strftime("%d%m%Y_%H%M") # Date
path = os.path.join("media", f"chat_{dt_string}")   # Path
os.mkdir(path)
os.chmod(path, 0o777) # Full access


#############################################
# FLASK WEB APP
#############################################
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

#############################################
# FLOW
#############################################
@app.route('/start')
def flow():
    manager = dm_core()
    # TODO: Create a start() function inside DM
    # This function should be connected to sp_recognition module
    # and get the audio converted to text to start flow.
    manager.start()  

#############################################
# MAIN
#############################################
if __name__ == "__main__":
    app.run() 

    