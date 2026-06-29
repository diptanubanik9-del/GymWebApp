from flask import Flask, render_template, request, redirect
import mysql.connector
import os

app = Flask(__name__)

def get_db():
    return mysql.connector.connect(
        host="sql12.freesqldatabase.com",
        user="sql12831826",
        password="MKjI6dpxxv",
        database="sql12831826"
    )

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
    if request.method =="POST":
        name = request.form["name"]
        db = get_db()
        cursor = db.cursor()
        cursor.execute("select * from members where name = %s", (name,))
        results = cursor.fetchall()
        cursor.close()
        db.close()
    return render_template("search.html", results=results)


@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
