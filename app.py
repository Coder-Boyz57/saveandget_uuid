from flask import Flask, render_template, request, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# MySQL database configuration
DB_CONFIG = {
    "host": "sql205.infinityfree.com",
    "user": "if0_38097969",
    "password": "T0UaXaM3GMFeH",
    "database": "if0_38097969_aiytm",
    "port": 3306
}

# Function to get a connection to the MySQL database
def get_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Initialize the database
def init_db():
    try:
        conn = get_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                id VARCHAR(255) PRIMARY KEY,
                                name VARCHAR(255),
                                email VARCHAR(255),
                                niche VARCHAR(255),
                                country VARCHAR(255))''')
            conn.commit()
            cursor.close()
            conn.close()
    except Error as e:
        print(f"Error initializing database: {e}")

init_db()

@app.route('/')
def index():
    search_query = request.args.get('search', '')

    try:
        conn = get_db()
        if not conn:
            return "Error: Could not connect to the database."

        cursor = conn.cursor(dictionary=True)

        if search_query:
            query = """SELECT * FROM users 
                       WHERE name LIKE %s OR email LIKE %s OR niche LIKE %s OR country LIKE %s 
                       LIMIT 10"""
            cursor.execute(query, (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
        else:
            cursor.execute("SELECT * FROM users")
        
        users = cursor.fetchall()
        conn.close()

        return render_template('index.html', users=users, search_query=search_query)
    except Error as e:
        return f"Error: {e}"

@app.route('/get_user')
def get_user():
    user_id = request.args.get('id')

    if not user_id:
        return jsonify({"error": "ID is required."})

    try:
        conn = get_db()
        if not conn:
            return jsonify({"error": "Could not connect to the database."})

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
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
        conn = get_db()
        if not conn:
            return jsonify({"error": "Could not connect to the database."})

        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (id, name, email, niche, country) VALUES (%s, %s, %s, %s, %s)",
                       (user_id, name, email, niche, country))
        conn.commit()
        conn.close()

        return jsonify({"id": user_id})
    except Error as e:
        return jsonify({"error": f"Failed to save data: {e}"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)
