from flask import Flask, render_template, request, session, flash, redirect, url_for
from functools import wraps
from validate import *
from dbhelper import *
import json

app = Flask(__name__)
with open('key', 'r') as f:
   app.secret_key = f.read().strip()

def redirect_if_not_logged_in(target):
    def wrap(func):
       @wraps(func)
       def inner(*args, **kwargs):
          if not session.has_key('email') or session['email'] == None:
             #flash ("You are not logged in!")
             #session.clear()
             return redirect(url_for(target))
          else:
             pass
          return func(*args, **kwargs)
       return inner
    return wrap

@app.route("/")
@redirect_if_not_logged_in("welcome")
def index():
    return render_template('index.html', loggedin=session.has_key("email"))

@app.route("/welcome", methods=['GET', 'POST'])
def welcome():
    if request.method=="POST":
        print request.form
        if request.form.has_key("register"):
            email = request.form['registerEmail1']
            password = request.form['registerPassword']
            phone = request.form['registerPhone']
            auth("register", email, password, phone)
        if request.form.has_key("login"):
            email = request.form['loginEmail']
            password = request.form['loginPassword']
            auth("login", email, password)
        return redirect(url_for("index"))
    else:
        return render_template('welcome.html', loggedin=session.has_key("email"))

@app.route("/geo", methods=["GET", "POST"])
def geo():
    return render_template('geo.html', loggedin=session.has_key("email"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=="POST" and request.form.has_key('password') \
      and request.form.has_key('email'):
        session ['email'] = None
        if is_valid_email(request['email']) and\
          is_valid_password(request['password']):
            flash("Good job.")
        else:
            flash("Bad job.")
    return render_template('login.html', loggedin=session.has_key("email"))

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html', loggedin=session.has_key("email"))

@app.route('/donate', methods=['GET'])
def donate():
    return render_template('donate.html', loggedin=session.has_key("email"))

@app.route('/api/add', methods=['POST'])
def add():
    print 'hey its works bub'
    uemail = session['email']
    latter = float(request.form['latitude'])
    longter = float(request.form['longitude'])
    utype = request.form['type']
    addPlace(utype, longter, latter, uemail)
    return 'Utility marked!'

@app.route('/api/get', methods=['POST'])
def get():#eventually will get nearby places
    return json.dumps(get_places())    

@app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for('index')), 404

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
