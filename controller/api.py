import os

from flask import Flask, jsonify, request

from model.iohelpers import ioHelpers
from model import defaults
from idents.logins import accs

app = Flask(__name__)

autoresponse_path = defaults.AUTORESPONSE_PATH
io_helper = ioHelpers(autoresponse_path)

@app.route('/discordbotapi', methods=['POST'])
def discord_bot_api():

    username = request.form.get('username')
    password_hash = request.form.get('password_hash')

    if username not in accs or accs[username] != password_hash:
        return jsonify({"Error": "This is not for you :P"}), 401

    if 'file' not in request.files:
        return jsonify({"Error":"No file included?? Amateur hour??"}), 415
    file = request.files['file']
    if file.filename == '':
        return jsonify({"Error":"No file name included?? HOW??"}), 415
    if file:
        print("Saving to:", autoresponse_path)
        final_path = os.path.join(autoresponse_path, file.filename)
        print("Final path:", final_path)
        if(io_helper.write_file(os.path.join(autoresponse_path, file.filename), file) == 0):
            return({"OK":"Wait up to 30 seconds for it to show up"}, 200)
        else:
            return jsonify({"Error":"Whoopsie daisy"}), 500


def run_api():
    app.run(port=5000, debug=True, use_reloader=False)