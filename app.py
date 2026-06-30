from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = "water123"
ADMIN_USERNAME = "malik"
ADMIN_PASSWORD = "water123"

def get_db():
    return mysql.connector.connect(
        host="sql12.freesqldatabase.com",
        user="sql12831826",
        password="MKjI6dpxxv",
        database="sql12831826"
    )
def login_required():
    return session.get("logged_in")

def admin_required():
    return session.get("is_admin")

@app.context_processor
def inject_login():
    return {
        "logged_in": login_required(),
        "is_admin": admin_required(),
    }

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/members")
def members():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Members")
    members = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("members.html", members=members)

@app.route("/add_member", methods=["GET", "POST"])
def add_member():
    if not admin_required():
        return redirect("/login")
    
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        phone = request.form["phone"]

        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO Members (name, age, gender, phone, join_date) VALUES (%s, %s, %s, %s, CURDATE())", (name, age, gender, phone))
        db.commit()
        cursor.close()
        db.close()

        return redirect("/members")

    return render_template("add_member.html")

@app.route("/delete_member/<id>")
def delete_member(id):
    if not admin_required():
        return redirect("/login")

    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Members WHERE member_id = %s", (id,))
    db.commit()
    cursor.close()
    db.close()
    return redirect("/members")

@app.route("/search", methods=["GET", "POST"])
def search():
    results = []
    if request.method == "POST":
        name = request.form["name"]
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Members WHERE name LIKE %s", (f"%{name}%",))
        results = cursor.fetchall()
        cursor.close()
        db.close()  # fixed!
    return render_template("search.html", results=results)


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if login_required():
        return redirect("/members")

    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        phone = request.form["phone"]
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT member_id FROM Members WHERE username = %s", (username,))
        if cursor.fetchone():
            cursor.close()
            db.close()
            return render_template("register.html", error="Username already taken")

        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO Members (name, age, gender, phone, username, password, join_date) VALUES (%s, %s, %s, %s, %s, %s, CURDATE())",
            (name, age, gender, phone, username, hashed_password),
        )
        db.commit()
        cursor.close()
        db.close()
        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if login_required():
        return redirect("/members")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["logged_in"] = True
            session["is_admin"] = True
            return redirect("/members")

        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT member_id, password FROM Members WHERE username = %s",
            (username,),
        )
        member = cursor.fetchone()
        cursor.close()
        db.close()

        if member and member[1] and check_password_hash(member[1], password):
            session["logged_in"] = True
            session["member_id"] = member[0]
            session["is_admin"] = False
            return redirect("/members")

        return render_template("login.html", error="Not registered or invalid password")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    session.pop("member_id", None)
    session.pop("is_admin", None)
    return redirect("/login")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
