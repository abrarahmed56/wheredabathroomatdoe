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
             flash ("You are not logged in!")
             session.clear()
             return redirect(url_for(target))
          else:
             pass
          return func(*args, **kwargs)
       return inner
    return wrap

@app.route("/")
@redirect_if_not_logged_in("welcome")
def index():
    return render_template('index.html')

@app.route("/welcome", methods=['GET', 'POST'])
def welcome():
    print "0"
    if request.method=="POST":
        print "other 1"
        print request.form
        email1 = request.form['email1']
        email2 = request.form['email2']
        if email1 != email2:
            flash("Please enter the same email")
        password = request.form['password']
        print "1"
        if request.form.has_key("register"):
            dbhelper.auth("register", email1, password)
            print "2"
        if request.form.has_key("login"):
            dbhelper.auth("login", email2, password)
            print "3"
        return redirect(url_for("index"))
        #return "loggedin"
    print "4"
    return render_template('welcome.html')

@app.route("/geo", methods=["GET", "POST"])#geolocation almost not broken lmoa
def geo():
    return render_template('geo.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
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
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')

@app.route('/donate', methods=['GET', 'POST'])
def donate():
    return render_template('donate.html')

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
