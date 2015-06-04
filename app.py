from flask import Flask, render_template, request, session, flash, redirect, url_for
from functools import wraps
from validate import *
from dbhelper import *
from constants import *
import json
import uuid
import os
from werkzeug import secure_filename
from PIL import Image

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = set(["png", "bmp", "jpg"])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
with open('key', 'r') as f:
   app.secret_key = f.read().strip()

def deflate_uuid(uuid):
    return uuid.replace('-', '')

def inflate_uuid(uuid):
    if len(uuid) == 32:
        return uuid[0:8] + '-' + uuid[8:12] + '-' + uuid[12:16] + '-' + uuid[16:20] + '-' + uuid[20:32]
    else:
        return None

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

@app.route('/')
@redirect_if_not_logged_in("welcome")
def index():
    return render_template('index.html', loggedin=session.has_key("email"))

@app.route('/welcome', methods=['GET', 'POST'])
def welcome():
    if request.method=="POST":
        if request.form.has_key("register"):
            required_keys = [ 'registerEmail1'
                            , 'registerPassword1'
                            , 'registerPhone'
                            ]
            if is_valid_request(request.form, required_keys):
                email = request.form['registerEmail1']
                password = request.form['registerPassword1']
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

@app.route('/geo', methods=['GET', 'POST'])
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

@app.route('/profile', methods=['GET'])
@redirect_if_not_logged_in("welcome")
def profile():
    return redirect('/profile/' + deflate_uuid(session['uid']))

@app.route('/profile/<userid>', methods=['GET'])
@redirect_if_not_logged_in("welcome")
def profile_with_id(userid):
    try:
        userid = inflate_uuid(userid)
        if userid:
            uid = uuid.UUID(userid)
            if uid_exists(uid):
                return render_template('profile.html',
                        loggedin=session.has_key("email"),
                        user_data = get_user_data(uid))
        flash("I c wut u did dere ;)")
        return redirect(url_for('index'))
    except ValueError, e:
        flash("I c wut u did dere ;)")
        return redirect(url_for('index'))

@app.route('/api/add', methods=['POST'])
def add():
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

def allowed_file(filename):
    return '.' in filename and filename.rsplit(".", 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and request.files.has_key('pic'):
        file = request.files['pic']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            try:
                img = Image.open(file.stream)
                img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                flash("Upload successful")
            except IOError:
                flash("Invalid image")
            return redirect(url_for('index'))
        flash("Upload unsuccessful")
    return render_template("upload_form.html")

@app.route('/settings/', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        required_keys = [ 'new_email'
                        , 'new_phone'
                        , 'new_password'
                        , 'new_firstname'
                        , 'new_lastname'
                        , 'new_bio'
                        , 'verify_password'
                        ]
        if is_valid_request(request.form, required_keys):
            uid = uuid.UUID(session['uid'])
            old_password = get_user_password(uid=uid)
            if old_password:
                if not validate.check_password(old_password,
                        request.form['verify_password']):
                    flash("Invalid verification credentials")
                else:
                    if session['email'] != request.form['new_email']:
                        validate_email = validate.is_valid_email(request.form['new_email'])
                        if validate_email[0]:
                            flash(update_user_email(uid,
                                request.form['new_email'])[1])
                        else:
                            flash(validate_email[1])
                    validate_phone = validate.is_valid_telephone(request.form['new_phone'])
                    if validate_phone[0]:
                        if validate_phone[1] != get_user_phone(uid):
                            flash(update_user_phone(uid, validate_phone[1])[1])
                    else:
                        flash(validate_email[1])
                    if request.form['new_password']:
                        validate_password = validate.is_valid_password(request.form['new_password'])
                        if validate_password[0]:
                            flash(update_user_password(uid, request.form['new_password'])[1])
                        else:
                            flash(validate_password[1])
                    if request.form['new_firstname'] != get_user_firstname(uid):
                        flash(update_user_firstname(uid,
                            request.form['new_firstname'])[1])
                    if request.form['new_lastname'] != get_user_lastname(uid):
                        flash(update_user_lastname(uid,
                            request.form['new_lastname'])[1])
                    if request.form['new_bio'] != get_user_bio(uid):
                        flash(update_user_bio(uid, request.form['new_bio'])[1])
            return render_template('settings.html', user_data=get_user_data(uid))
        else:
            flash("Malformed request")
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
