from flask import Flask, render_template, request, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# MySQL database connection details
DB_CONFIG = {
    'host': 'sql12.freesqldatabase.com',
    'database': 'sql12755602',
    'user': 'sql12755602',
    'password': 'gfes9gyk8A',
    'port': 3306
}

# Function to create a database connection
def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        raise Exception(f"Error connecting to database: {e}")

# Initialize the database and create the users table if it doesn't exist
def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                niche VARCHAR(255) NOT NULL,
                country VARCHAR(255) NOT NULL
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error initializing database: {e}")

# Initialize the database
init_db()

@app.route('/')
def index():
    search_query = request.args.get('search', '')

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if search_query:
            query = """
                SELECT * FROM users 
                WHERE name LIKE %s OR email LIKE %s OR niche LIKE %s OR country LIKE %s
            """
            cursor.execute(query, (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"))
        else:
            cursor.execute("SELECT * FROM users")

        users = cursor.fetchall()
        cursor.close()
        conn.close()

        return render_template('index.html', users=users, search_query=search_query)
    except Error as e:
        return f"Error: {e}"

@app.route('/get_user')
def get_user():
    user_id = request.args.get('id')

    if not user_id:
        return jsonify({"error": "UUID is required."})

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            return jsonify(user)
        else:
            return jsonify({"error": "User not found."})
    except Error as e:
        return jsonify({"error": f"Failed to retrieve data: {e}"})

@app.route('/save_user', methods=['POST'])
def save_user():
    name = request.form.get('name')
    email = request.form.get('email')
    niche = request.form.get('niche')
    country = request.form.get('country')

    if not name or not email or not niche or not country:
        return jsonify({"error": "All fields (name, email, niche, country) are required."})

    user_id = f"uuid-{str(hash(name + email))}"  # Simulating UUID generation

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Try to insert or replace the user data
        query = """
            INSERT INTO users (id, name, email, niche, country)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                email = VALUES(email),
                niche = VALUES(niche),
                country = VALUES(country)
        """
        cursor.execute(query, (user_id, name, email, niche, country))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"id": user_id})
    except Error as e:
        return jsonify({"error": f"Failed to save data: {e}"})

if __name__ == '__main__':
    app.run(host="0.0.0.0")
