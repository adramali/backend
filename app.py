from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import os  # Import os module here
from flask_cors import CORS  # Import CORS

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Enable CORS for all domains
CORS(app)  # This allows all origins to access your API

# Alternatively, you can specify specific origins:
# CORS(app, resources={r"/signup": {"origins": "http://localhost:3000"}})

# Fetch database credentials from environment variables
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

# Initialize MySQL connection
mysql = MySQL(app)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    print("Received data:", data)  # Log received data for debugging

    full_name = data.get('full_name')
    email = data.get('email')
    phone_number = data.get('phone_number')
    dob = data.get('dob')
    password = data.get('password')
    confirmPassword = data.get('confirmPassword')

    # Validate input
    if not full_name or not email or not password or not confirmPassword:
        return jsonify({"message": "All fields are required!"}), 400

    if password != confirmPassword:
        return jsonify({"message": "Passwords do not match!"}), 400

    # Hash the password
    hashed_password = generate_password_hash(password)

    # Create cursor
    cursor = mysql.connection.cursor()

    try:
        # Check if email already exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({"message": "Email already exists!"}), 400

        # Insert new user into the database
        cursor.execute(
            "INSERT INTO users (full_name, email, phone_number, dob, password) VALUES (%s, %s, %s, %s, %s)",
            (full_name, email, phone_number, dob, hashed_password)
        )

        # Commit changes
        mysql.connection.commit()

        # Close cursor
        cursor.close()

        return jsonify({"message": "Signup successful!"}), 201

    except Exception as e:
        print("Error:", e)  # Log the full error message for debugging
        mysql.connection.rollback()  # Rollback in case of error
        return jsonify({"message": "An error occurred. Please try again later."}), 500

if __name__ == '__main__':
    app.run(debug=True)
