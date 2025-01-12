from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# SQLite database setup
DATABASE = 'users.db'

# Initialize the database
def init_db():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE users (
                            id TEXT PRIMARY KEY,
                            name TEXT,
                            email TEXT,
                            niche TEXT,
                            country TEXT)''')
        conn.commit()
        conn.close()

# Function to get a connection to the database
def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

# Initialize the database
init_db()

@app.route('/')
def index():
    search_query = request.args.get('search', '')

    try:
        conn = get_db()
        cursor = conn.cursor()

        if search_query:
            cursor.execute("SELECT * FROM users WHERE name LIKE ? OR email LIKE ? OR niche LIKE ? OR country LIKE ? LIMIT 10", 
                           (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
        else:
            cursor.execute("SELECT * FROM users")
        
        users = cursor.fetchall()
        conn.close()

        return render_template('index.html', users=users, search_query=search_query)
    except Exception as e:
        return f"Error: {e}"

@app.route('/get_user')
def get_user():
    user_id = request.args.get('id')

    if not user_id:
        return jsonify({"error": "ID is required."})

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            return jsonify({
                "id": user[0],
                "name": user[1],
                "email": user[2],
                "niche": user[3],
                "country": user[4]
            })
        else:
            return jsonify({"error": "User not found."})
    except Exception as e:
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
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (id, name, email, niche, country) VALUES (?, ?, ?, ?, ?)",
                       (user_id, name, email, niche, country))
        conn.commit()
        conn.close()

        return jsonify({"id": user_id})
    except Exception as e:
        return jsonify({"error": f"Failed to save data: {e}"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)
