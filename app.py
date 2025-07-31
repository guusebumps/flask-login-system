from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "3e60b6aec3ffa3cc1c79dfaee3f94b1c36cd71b5a2a3a76d978d74f5b70aef57"

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        role = request.form["role"]

        try:
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                           (username, password, role))
            conn.commit()
            conn.close()
            flash("Usuário registrado com sucesso!", "success")
            return redirect(url_for("home"))
        except:
            flash("Erro: usuário já existe!", "danger")
    return render_template("register.html")

# Login
@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[2], password):
        session["username"] = user[1]
        session["role"] = user[3]
        return redirect(url_for("dashboard"))
    else:
        flash("Usuário ou senha inválidos!", "danger")
        return redirect(url_for("home"))

# Dashboard com permissões
@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("home"))

    role = session["role"]

    if role == "admin":
        return render_template("dashboard.html", user=session["username"], role="Administrador")
    elif role == "moderator":
        return render_template("dashboard.html", user=session["username"], role="Moderador")
    else:
        return render_template("dashboard.html", user=session["username"], role="Usuário comum")

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
