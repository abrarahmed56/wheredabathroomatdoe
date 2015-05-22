from flask import Flask, render_template, request, session, flash, redirect, url_for
from functools import wraps
from validate import *
import dbhelper

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
    loggedin = session.has_key("email")
    return render_template('index.html', loggedin=True)

@app.route("/welcome", methods=['GET', 'POST'])
def welcome():
    loggedin = session.has_key("email")
    print "0"
    if request.method=="POST":
        print "other 1"
        print request.form
        print "1"
        if request.form.has_key("register"):
            email = request.form['registerEmail1']
            password = request.form['registerPassword']
            dbhelper.auth("register", email, password)
            print "2"
        if request.form.has_key("login"):
            email = request.form['loginEmail']
            password = request.form['loginPassword']
            dbhelper.auth("login", email, password)
            print "3"
        return redirect(url_for("index"))
        #return "loggedin"
    print "4"
    return render_template('welcome.html', loggedin=loggedin)

@app.route("/geo", methods=["GET", "POST"])#geolocation almost not broken lmoa
def geo():
    loggedin = session.has_key("email")
    return render_template('geo.html', loggedin)

@app.route('/login', methods=['GET', 'POST'])
def login():
    loggedin = session.has_key("email")
    session ['email'] = None
    if request.method=="POST" and request.form.has_key('password') \
      and request.form.has_key('email'):
       if not is_valid_email(request['email']):
          flash("Good job.")
       else:
          flash("Bad job.")
       if not is_valid_password(request['password']):
          flash("Good job.")
       else:
          flash("Bad job.")
    return render_template('login.html', loggedin=loggedin)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route('/about', methods=['GET', 'POST'])
def about():
    loggedin = session.has_key("email")
    return render_template('about.html', loggedin=loggedin)

@app.route('/donate', methods=['GET', 'POST'])
def donate():
    loggedin = session.has_key("email")
    return render_template('donate.html', loggedin=loggedin)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
