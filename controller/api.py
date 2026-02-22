import os

from flask import Flask, jsonify, request, send_from_directory
from functools import wraps
import base64

import jwt
from jwt import encode, decode

import datetime

from model.api_db import *
from dotenv import load_dotenv

PROJECT_ROOT = os.getcwd()

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('JWT_SECRET', os.getenv('SECRET_KEY'))
app.config["JSON_SORT_KEYS"] = False

@app.teardown_appcontext
def teardown_db(exception):
    close_db(exception)

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        data = request.get_json(silent=True) or {}

        # 1) Try JWT in Authorization header: Bearer <jwt>
        auth_header = request.headers.get('Authorization', '')
        username = None
        password_hash = None
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1].strip()
            try:
                payload = decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
                username = payload.get('sub')
                print("Username from JWT:", username)
                return f(*args, **kwargs)  # If JWT is valid, proceed immediately
            except jwt.ExpiredSignatureError:
                return jsonify({"Error": "Token expired"}), 401
            except Exception:
                # not a JWT we can decode; fall back to previous methods
                username = None

        # 2) Fallback: Authorization header carrying base64(username:password_hash), JSON body, or custom headers
        if not username:
            # legacy: Authorization: Bearer <base64(username:password_hash)>
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ', 1)[1].strip()
                try:
                    decoded = base64.b64decode(token).decode('utf-8')
                    if ':' in decoded:
                        username, password_hash = decoded.split(':', 1)
                except Exception:
                    pass

        if not username or not password_hash:
            username = username or data.get('username') or request.headers.get('X-Username')
            password_hash = password_hash or data.get('password_hash') or request.headers.get('X-Password-Hash')

        if not username or (not password_hash and not auth_header.startswith('Bearer ')) or not check_auth(username, password_hash if password_hash else ""):
            return jsonify({"Error": "Urkullupitxon identifícate"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/TelekApp/discordbotapi', methods=['POST'])
@requires_auth
def discord_bot_api():
    data = request.get_json()
    if not data:
        return jsonify({"Error": "nena pero dame info"}), 400

    # Required fields
    trigger = data.get('trigger').lower()
    autoresponse = data.get('autoresponse')
    if not trigger or not autoresponse:
        return jsonify({"Error": "nena pero dime a que responder"}), 400

    # Save to database
    try:
        idTrigger = create_trigger(trigger)
        idResponse = create_response(autoresponse)
        create_combo(idTrigger, idResponse)
    except Exception as e:
        print("Error saving to database:", e)
        return jsonify({"Error": "Failed to save to database"}), 500

    return jsonify({"Success": "omg cafecito lo hiciste!"}), 200

@app.route('/TelekApp/autoresponse', methods=['GET'])
@requires_auth
def get_all_combos_route():
    return jsonify(get_combos()), 200

@app.route('/TelekApp/autoresponse/<trigger>', methods=['GET'])
@requires_auth
def get_combos_by_trigger_route(trigger):
    combo = get_combos(trigger_content=trigger)

    if combo:
        return jsonify(combo), 200
    else:
        return jsonify({"error": "Trigger not found"}), 404
    
@app.route('/TelekApp/autoresponse/delete', methods=['POST'])
@requires_auth
def delete_combo_route():
    data = request.get_json()
    trigger = data.get('trigger')
    response = data.get('response')
    if not trigger or not response:
        print("Nothing")
        return jsonify({"error": "No trigger or response provided"}), 400

    try:
        delete_combo(trigger, response)
        print("OK")
        return jsonify({"message": "Combo deleted successfully"}), 200
    except Exception as e:
        print("COCK")
        return jsonify({"error": f"Failed to delete combo: {str(e)}"}), 500
    
@app.route('/TelekApp/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password_hash = data.get('password_hash')
    print(f"{username} && {password_hash}")
    if not username or not password_hash:
        return jsonify({"error": "No username or password_hash provided"}), 400
    # Authenticate credentials
    if not check_auth(username, password_hash):
        return jsonify({"error": "Invalid credentials"}), 401

    # Create JWT
    try:
        now = datetime.datetime.utcnow()
        exp = now + datetime.timedelta(hours=12)
        payload = {
            'sub': username,
            'iat': now,
            'exp': exp
        }
        token = encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
        print("here")
        return jsonify({"access_token": token, "token_type": "bearer", "expires_at": exp.isoformat() + 'Z'}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to create token: {str(e)}"}), 500
    
@app.route('/TelekApp/check_token' , methods=['GET'])
def auth():
    token = request.headers.get('Authorization', '').split('Bearer ')[-1].strip()
    if not token:
        return jsonify({"error": "No token provided"}), 400

    try:
        payload = decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        username = payload.get('sub')
        if not username:
            return jsonify({"error": "Invalid token"}), 401
        return jsonify({"valid": True}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except Exception as e:
        return jsonify({"error": f"Failed to authenticate token: {str(e)}"}), 500
    
@app.route('/TelekApp/', methods=['GET'])
def index():
    return send_from_directory(os.path.join(PROJECT_ROOT, 'view'), 'index.html')

# Serve static files (JS, CSS, images)
@app.route('/TelekApp/<path:filename>')
def static_files(filename):
    return send_from_directory(os.path.join(PROJECT_ROOT, 'view'), filename)
    
@app.route('/TelekApp/register', methods=['POST'])
@requires_auth
def  register():
    data = request.get_json()
    username = data.get('username_reg')
    password_hash = data.get('password_hash_reg')
    try:
        new_user(username, password_hash)
        return jsonify({"message": "User registered successfully"}), 200
    except Exception as e:
        return jsonify({"error":f"ha ocurrido un extraño suseso"}), 500


def check_auth(username, password_hash):
    return authenticate(username, password_hash)

def run_api():
    app.run(port=5000, debug=False, use_reloader=False)

