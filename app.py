from flask import Flask, render_template, request, session
from pymongo import Connection
import json, random
from bson.objectid import ObjectId

app = Flask(__name__)
conn = Connection()
db = conn['c']

@app.route("/")
def home():
    if ('username' not in session or session.get('username') == None):
        flash ("You are not logged in!")
        return redirect("/login")
    return render_template("index.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if ('username' not in session):
        session ['username'] = None
    if (session.get('username') != None):
        flash ("You are already logged in!")
        return redirect("/")
    session ['username'] = None
    submit = request.args.get("submit")
    if (submit == "Submit"):
        username = request.args.get("username")
        password = request.args.get("password")
        does_account_exist = db.user_auth(username, password);
        if (does_account_exist == True):
            session ['username'] = username
            return redirect("/")
        flash ("Invalid Username or Password")
        return redirect ("/login")
    return render_template ("login.html")
    
if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=1776)
