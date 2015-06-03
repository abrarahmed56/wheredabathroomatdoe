from flask import Flask, render_template, request, session, flash, redirect, url_for
from functools import wraps
from validate import *
from dbhelper import *
from constants import *
import json
import uuid

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
            required_keys = [ 'registerEmail1'
                            , 'registerPassword'
                            , 'registerPhone'
                            ]
            if is_valid_request(request.form, required_keys):
                email = request.form['registerEmail1']
                password = request.form['registerPassword']
                phone = request.form['registerPhone']
                flash(auth(AUTH_REGISTER, email, password, phone))
            else:
                flash("Malformed request")
        elif request.form.has_key("login"):
            required_keys = [ 'loginEmail'
                            , 'loginPassword'
                            ]
            if is_valid_request(request.form, required_keys):
                email = request.form['loginEmail']
                password = request.form['loginPassword']
                flash(auth(AUTH_LOGIN, email, password))
            else:
                flash("Malformed request")
        return redirect(url_for("index"))
    else:
        return render_template('welcome.html', loggedin=session.has_key("email"))

@app.route("/geo", methods=["GET", "POST"])
def geo():
    return render_template('geo.html', loggedin=session.has_key("email"))

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash("Logout successful")
    return redirect(url_for("index"))

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html', loggedin=session.has_key("email"))

@app.route('/donate', methods=['GET'])
def donate():
    return render_template('donate.html', loggedin=session.has_key("email"))

@app.route('/profile', methods=['POST'])
@redirect_if_not_logged_in("welcome")
def profile():
    bio = get_user_bio(None,session["email"])
    return render_template('profile.html', loggedin=session.has_key("email"), bio=bio)

@app.route('/api/add', methods=['POST'])
def add():
    print 'hey its works bub'
    uemail = session['email']
    latter = float(request.form['latitude'])
    longter = float(request.form['longitude'])
    utype = request.form['type']
    add_place(utype, longter, latter, uemail)
    return 'Utility marked!'

@app.route('/api/get', methods=['POST'])
def get():#eventually will get nearby places
    return json.dumps(get_places())
    #return json.dumps(get_local_places(location_x, location_y, radius))

@app.route('/settings/', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        pass
    else:
        return render_template('settings.html',
                               user_data=get_user_data(uuid.UUID(session['uid'])))

@app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for('index')), 404

def is_valid_request(form, required_keys):
    for key in required_keys:
        if not form.has_key(key):
            return False
    return True

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
