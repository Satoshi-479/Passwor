from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "my_super_secret_key" # Keep this for session security
DATABASE_FILE = "passwords.db"
MASTER_PWD_FILE = "master.pwd"

# Ensure database exists with correct columns
def init_db():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            website TEXT NOT NULL,
            username TEXT,
            phone_number TEXT,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    db = get_db()
    rows = db.execute("SELECT * FROM passwords").fetchall()
    db.close()
    return render_template('index.html', passwords=rows)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Check if master.pwd exists, if not, create it with user's first input
        user_input = request.form.get('master_password')
        if not os.path.exists(MASTER_PWD_FILE):
            with open(MASTER_PWD_FILE, "w") as f:
                f.write(user_input)
        
        with open(MASTER_PWD_FILE, "r") as f:
            stored = f.read().strip()
            
        if user_input == stored:
            session['logged_in'] = True
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/add', methods=['POST'])
def add():
    site = request.form.get('website')
    user = request.form.get('username')
    phone = request.form.get('phone')
    pwd = request.form.get('password')
    
    db = get_db()
    db.execute("INSERT INTO passwords (website, username, phone_number, password) VALUES (?, ?, ?, ?)",
               (site, user, phone, pwd))
    db.commit()
    db.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete(id):
    db = get_db()
    db.execute("DELETE FROM passwords WHERE id = ?", (id,))
    db.commit()
    db.close()
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
