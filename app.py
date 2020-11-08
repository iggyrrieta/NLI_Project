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
#            GLOBAL CONFIG        
#############################################

# CREATE LOCAL FOLDER WITH PERMISSION 
now = datetime.now()
dt_string = now.strftime("%d%m%Y_%H%M") # Date
path = os.path.join("media", f"chat_{dt_string}")   # Path
os.mkdir(path)
os.chmod(path, 0o777) # Full access

# config
config = {
    'app': {
        'title': 'TOURIST GUIDE ASSISTANT',
        'description': 'Simple agent using Flask'
    }
}

# Get DIALOGUE MANAGER
manager = DMCore()
#############################################
# FLASK WEB APP
#############################################
app = Flask(__name__)

@app.route("/", methods=['GET'])
def home():
    return render_template("chat.html", data=config['app'], log=start())

# TODO this is not working as expected, the agent works but
# the history log is not displayed on the screen...
# TODO The manual input isn't working either...
@app.route('/start', methods=['POST'])
def start():
    log_history = []
    if request.method == 'POST':
        # Start application
        manager.start(path) 
        # Enable manual messages
        enable = request.form['enable_manual']
        message = request.form['message']

        if enable:
            manager.manual_input(message)

        log_history = manager.history

    return log_history

#############################################
# MAIN
#############################################
if __name__ == "__main__":
    app.config['SECRET_KEY'] = '55edbe0d60d60af5c2b54d8a' 
    app.run(host=os.getenv('IP', '0.0.0.0'), 
            port=int(os.getenv('PORT', 4444)))

    