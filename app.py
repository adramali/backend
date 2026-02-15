from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
from flask_cors import CORS
import traceback

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# DB config - ensure these env vars are set in your environment/.env
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
# return rows as dicts (easier to work with)
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# health check that also attempts a trivial DB query
@app.route('/health', methods=['GET'])
def health():
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT 1 AS ok')
        cur.fetchone()
        cur.close()
        return jsonify({"status": "ok"}), 200
    except Exception:
        # print full traceback to server logs
        print('DB health check failed:')
        traceback.print_exc()
        return jsonify({"status": "db-error"}), 500

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    print("Received data:", data)

    full_name = data.get('full_name')
    email = data.get('email')
    phone_number = data.get('phone_number')
    dob = data.get('dob')
    password = data.get('password')
    confirmPassword = data.get('confirmPassword')

    if not full_name or not email or not password or not confirmPassword:
        return jsonify({"message": "All fields are required!"}), 400

    if password != confirmPassword:
        return jsonify({"message": "Passwords do not match!"}), 400

    hashed_password = generate_password_hash(password)

    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        existing_user = cur.fetchone()

        if existing_user:
            return jsonify({"message": "Email already exists!"}), 400

        cur.execute(
            "INSERT INTO users (full_name, email, phone_number, dob, password) VALUES (%s, %s, %s, %s, %s)",
            (full_name, email, phone_number, dob, hashed_password)
        )
        mysql.connection.commit()
        return jsonify({"message": "Signup successful!"}), 201

    except Exception:
        print("Signup error:")
        traceback.print_exc()
        mysql.connection.rollback()
        return jsonify({"message": "An error occurred. Please try again later."}), 500

    finally:
        try:
            cur.close()
        except Exception:
            pass

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email and password required"}), 400

    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT id, password FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        if not user:
            return jsonify({"message": "Invalid credentials"}), 401

        stored_hash = user.get('password') if isinstance(user, dict) else user[1]
        if not check_password_hash(stored_hash, password):
            return jsonify({"message": "Invalid credentials"}), 401

        return jsonify({"message": "Login successful", "user_id": user.get('id') if isinstance(user, dict) else user[0]}), 200

    except Exception:
        print("Login error:")
        traceback.print_exc()
        return jsonify({"message": "An error occurred. Please try again later."}), 500

    finally:
        try:
            cur.close()
        except Exception:
            pass

if __name__ == '__main__':
    # simple startup check of env vars
    required = ['MYSQL_HOST', 'MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_DB']
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        print("Missing env vars:", missing)
    app.run(debug=True)
