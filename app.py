from flask import Flask, render_template, request, jsonify
import sqlite3
from sqlite3 import Error

app = Flask(__name__)

# SQLite database file path
DATABASE = 'aiytm_data.db'

# Function to create a database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This allows us to access columns by name
    return conn

# Initialize the database and create the users table if it doesn't exist
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            niche TEXT NOT NULL,
            country TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Initialize the database
init_db()

@app.route('/')
def index():
    search_query = request.args.get('search', '')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if search_query:
            cursor.execute("SELECT * FROM users WHERE name LIKE ? OR email LIKE ? OR niche LIKE ? OR country LIKE ?", 
                           ('%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%'))
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
        return jsonify({"error": "UUID is required."})
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            return jsonify({
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "niche": user["niche"],
                "country": user["country"]
            })
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
        cursor.execute("INSERT INTO users (id, name, email, niche, country) VALUES (?, ?, ?, ?, ?)", 
                       (user_id, name, email, niche, country))
        conn.commit()
        conn.close()

        return jsonify({"id": user_id})
    except Error as e:
        return jsonify({"error": f"Failed to save data: {e}"})

if __name__ == '__main__':
    app.run(host="0.0.0.0")
