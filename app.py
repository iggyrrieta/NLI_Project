from flask import Flask, render_template, request # Web app
from datetime import datetime # to create folder with date

import sys
import os


# ROOT FOLDER : Make things easier setting the root folder as the origin
root_path = os.getcwd()
sys.path.insert(0, f'{root_path}/NLI_Project')

# DM
from dm_core.main import DMCore

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
    manager = DMCore()
    # TODO: Create a start() function inside DM
    # This function should be connected to sp_recognition module
    # and get the audio converted to text to start flow.
    manager.start(path)

#############################################
# MAIN
#############################################
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
