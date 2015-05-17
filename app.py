from flask import Flask, render_template, request, session, flash, redirect, url_for
from functools import wraps
from validate import *

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
    if request.method=="POST":
        if request.form.has_key("login"):
            flash("Login successful")
        if request.form.has_key("register"):
            flash("Registration successful")
        session['email'] = request.form["email"]
        return redirect(url_for("index"))
        #return "loggedin"
    #return "welcome"
    return render_template('welcome.html')

@app.route("/geo", methods=["GET", "POST"])#geolocation almost not broken lmoa
def geo():
    return render_template('geo.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    session ['email'] = None
    # TODO use POST for login
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

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
