from flask import Flask, render_template, request # Web app
import os # to save/open files 
from datetime import datetime # to create folder with date

import sys
sys.path.insert(0, 'imutils/')
import dmanager

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
    manager = dmanager.Dmanager(path)
    manager.start()

#############################################
# MAIN
#############################################
if __name__ == "__main__":
    app.run() 

    