from flask import Flask, render_template, request, session, flash, redirect, url_for
from functools import wraps

app = Flask(__name__)
with open('key', 'r') as f:
   app.secret_key = f.read().strip()

def redirect_if_not_logged_in(target):
    def wrap(func):
       def inner(*args, **kwargs):
          if not session.has_key('username') or session['username'] == None:
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

@app.route("/welcome")
def welcome():
    return render_template("welcome.html")

@app.route("/geo", methods=["GET", "POST"])#geolocation almost not broken lmoa
def geo():
    return render_template('geo.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    session ['username'] = None
    # TODO use POST for login
    submit = request.args.get('submit')
    if submit == 'Submit':
        username = request.args.get('username')
        password = request.args.get('password')
        does_account_exist = db.user_auth(username, password);
        if does_account_exist:
            session ['username'] = username
            return redirect(url_for('index'))
        flash ("Invalid Username or Password")
        return redirect(url_for('login'))
    return render_template('login.html')
    
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=1776)
