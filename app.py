from flask import Flask, render_template, request, session, flash, redirect, url_for
from flask_limiter import Limiter
from functools import wraps
import validate
import users_dbhelper as usersdb
import places_dbhelper as placesdb
import reviews_dbhelper as reviewsdb
import favorites_dbhelper as favoritesdb
import temporaryurls_dbhelper as tmpurldb
import dbhelper
import emailhelper
from constants import *
from utils import *
import json
import uuid
import os
import sys
from werkzeug import secure_filename
from PIL import Image

app = Flask(__name__)
app.debug = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
with open('key', 'r') as f:
   app.secret_key = f.read().strip()

if not os.path.isfile('emailpassword'):
    print "emailpassword file is missing!"
    sys.exit(1)

limiter = Limiter(app)

def redirect_if_not_logged_in(target, show_flash=True):
    def wrap(func):
        @wraps(func)
        def inner(*args, **kwargs):
            if not session.has_key('email') or session['email'] == None:
                clear_session_login_data(session)
                if show_flash:
                    flash("You are not logged in!")
                return redirect(url_for(target))
            else:
                pass
            return func(*args, **kwargs)
        return inner
    return wrap

def redirect_if_logged_in(target):
    def wrap(func):
        @wraps(func)
        def inner(*args, **kwargs):
            if session.has_key('email') and session['email'] != None:
                return redirect(url_for(target))
            else:
                pass
            return func(*args, **kwargs)
        return inner
    return wrap

@app.route('/')
@limiter.limit("10 per minute", error_message="BRO, YOU GOTTA CHILL")
@redirect_if_not_logged_in("welcome", show_flash=False)
def index():
    return render_template('index.html', loggedin=True)

@app.route('/welcome', methods=['GET', 'POST'])
@limiter.limit("10 per minute", error_message="BRO, YOU GOTTA CHILL")
@redirect_if_logged_in("index")
def welcome():
    if request.method=="POST":
        if request.form.has_key("register"):
            required_keys = [ 'registerEmail1'
                            , 'registerPassword1'
                            , 'registerPhone'
                            , 'sourceUrl'
                            ]
            if is_valid_request(request.form, required_keys) and\
              request.form['sourceUrl']:
                email = request.form['registerEmail1']
                password = request.form['registerPassword1']
                phone = request.form['registerPhone']
                result = dbhelper.auth(AUTH_REGISTER, session, email, password,
                        phone)
                flash(result[1])
                if result[0]:
                    return redirect(url_for('welcome'))
            else:
                return "Malformed request"
        elif request.form.has_key("reset_password"):
            required_keys = [ 'forgotEmail'
                            , 'sourceUrl'
                            ]
            if is_valid_request(request.form, required_keys) and\
              request.form['sourceUrl']:
                email = request.form['forgotEmail']
                uid = usersdb.get_user_id(email)
                can_send_email = tmpurldb.add_temporary_url(uid,
                        TEMP_URL_PASSWORD_RESET)
                if can_send_email[0]:
                    url_id = deflate_uuid(str(can_send_email[1]))
                    flash(emailhelper.send_password_reset_email(email,
                        usersdb.get_user_firstname(uid), url_id))
            else:
                return "Malformed request"
        elif request.form.has_key("login"):
            required_keys = [ 'loginEmail'
                            , 'loginPassword'
                            , 'sourceUrl'
                            ]
            if is_valid_request(request.form, required_keys) and\
              request.form['sourceUrl']:
                email = request.form['loginEmail']
                password = request.form['loginPassword']
                result = dbhelper.auth(AUTH_LOGIN, session, email, password)
                flash(result[1])
                if result[0]:
                    return redirect(url_for('index'))
            else:
                flash("Malformed request")
        return render_template('redirect.html', url=request.form['sourceUrl'])
    else:
        return render_template('welcome.html',
                loggedin=session.has_key("email"))

@app.route('/geo', methods=['GET', 'POST'])
@limiter.limit("10 per minute", error_message="BRO, YOU GOTTA CHILL")
def geo():
    return render_template('geo.html', loggedin=session.has_key("email"))

@app.route('/logout', methods=['POST'])
@redirect_if_not_logged_in("welcome")
def logout():
    session.clear()
    flash("Logout successful")
    return redirect(url_for("index"))

@app.route('/about', methods=['GET'])
@limiter.limit("10 per minute", error_message="BRO, YOU GOTTA CHILL")
def about():
    return render_template('about.html', loggedin=session.has_key("email"))

@app.route('/donate', methods=['GET'])
@limiter.limit("10 per minute", error_message="BRO, YOU GOTTA CHILL")
def donate():
    return render_template('donate.html', loggedin=session.has_key("email"))

@app.route('/profile', methods=['GET'])
@limiter.limit("10 per minute", error_message="BRO, YOU GOTTA CHILL")
@redirect_if_not_logged_in("welcome")
def profile():
    return redirect('/profile/' + deflate_uuid(session['uid']))

@app.route('/profile/<userid>', methods=['GET'])
@limiter.limit("10 per minute", error_message="BRO, YOU GOTTA CHILL")
@redirect_if_not_logged_in("welcome")
def profile_with_id(userid):
    try:
        userid = inflate_uuid(userid)
        if userid:
            uid = uuid.UUID(userid)
            if usersdb.uid_exists(uid):
                return render_template('profile.html',
                        loggedin=True,
                        user_data=usersdb.get_user_data(uid))
        flash("I c wut u did dere ;)")
        return redirect(url_for('index'))
    except ValueError, e:
        flash("I c wut u did dere ;)")
        return redirect(url_for('index'))

@app.route('/profile/<userid>/report', methods=['POST'])
@limiter.limit("2 per minute", error_message="BRO, YOU GOTTA CHILL")
@redirect_if_not_logged_in("welcome")
def report_user(userid):
    # TODO implement reason for report
    try:
        userid = inflate_uuid(userid)
        if userid:
            uid = uuid.UUID(userid)
            reporter_id = uuid.UUID(session['uid'])
            if usersdb.uid_exists(uid):
                if usersdb.can_user_be_reported(reporter_id, uid):
                    flash(usersdb.add_user_report(reporter_id, uid,
                        "No reason")[1])
                    return redirect(url_for('profile_with_id',
                        userid=deflate_uuid(userid)))
        flash("I c wut u did dere ;)")
        return redirect(url_for('index'))
    except ValueError, e:
        flash("I c wut u did dere ;)")
        return redirect(url_for('index'))

@app.route('/api/add', methods=['POST'])
@limiter.limit("3 per minute", error_message="BRO, YOU GOTTA CHILL")
@redirect_if_not_logged_in("welcome")
def add():
    email = session['email']
    required_keys = [ 'latitude'
                    , 'longitude'
                    , 'type'
                    ]
    if is_valid_request(request.form, required_keys):
        try:
            latitude = float(request.form['latitude'])
            longitude = float(request.form['longitude'])
            util_type = request.form['type']
            if util_type in ALLOWED_TYPES:
                placesdb.add_place(util_type, longitude, latitude, email, '')
            else:
                return "Malformed Request"
        except ValueError:
            return "Malformed Request"
    else:
        return "Malformed Request"
    return 'Utility marked!'

# TODO consolidate api calls to a single request
@app.route('/api/getreviews', methods=['POST'])
@limiter.limit("30 per minute", error_message="BRO, YOU GOTTA CHILL")
def get_reviews_front_end():
    required_keys = [ 'placeType'
                    , 'locationX'
                    , 'locationY'
                    ]
    if is_valid_request(request.form, required_keys):
        uid = uuid.UUID(session['uid'])
        reviews = reviewsdb.get_reviews(
                placesdb.get_place_id(request.form['placeType'],
                    request.form['locationX'], request.form['locationY']))
        data = []
        for review in reviews:
            data.append({ "userFirstName" : usersdb.get_user_firstname(review[3])
                        , "rating" : review[4]
                        , "review" : review[5]
                        , "userProfile" : usersdb.get_user_profile_url(review[3])
                        , "userPic" : usersdb.get_user_profile_pic_url(review[3],
                                                                       128)
                        , "isRatable" : review[3] != uid
                        })
        return json.dumps(data)
    else:
        return "Malformed request"

@app.route('/api/addfavorite', methods=['POST'])
@limiter.limit("10 per minute", error_message="BRO, YOU GOTTA CHILL")
def add_favorite_front_end():
    user_id = uuid.UUID(session['uid'])
    required_keys = [ 'placeType'
                    , 'locationX'
                    , 'locationY'
                    ]
    if is_valid_request(request.form, required_keys):
        # FIXME needs float conversion of locationX and locationY
        place_id = placesdb.get_place_id(request.form['placeType'],
                request.form['locationX'], request.form['locationY'])
        return favoritesdb.add_favorite(user_id, place_id)
    else:
        return "Malformed request"

@app.route('/api/removefavorite', methods=['POST'])
@limiter.limit("10 per minute", error_message="BRO, YOU GOTTA CHILL")
def remove_favorite_front_end():
    user_id = uuid.UUID(session['uid'])
    required_keys = [ 'placeType'
                    , 'locationX'
                    , 'locationY'
                    ]
    if is_valid_request(request.form, required_keys):
        # FIXME wrap float conversion in a try-except block
        place_id = placesdb.get_place_id(request.form['placeType'],
               float(request.form['locationX']),
               float(request.form['locationY']))
        return favoritesdb.remove_favorite(user_id, place_id)
    else:
        return "Malformed request"

@app.route('/api/infavorites', methods=['POST'])
@limiter.limit("30 per minute", error_message="BRO, YOU GOTTA CHILL")
def in_favorites_front_end():
    user_id = uuid.UUID(session['uid'])
    required_keys = [ 'placeType'
                    , 'locationX'
                    , 'locationY'
                    ]
    if is_valid_request(request.form, required_keys):
        # FIXME needs float conversion
        place_id = placesdb.get_place_id(request.form['placeType'],
                request.form['locationX'], request.form['locationY'])
        return favoritesdb.in_favorites(user_id, place_id)
    else:
        return "Malformed request"

@app.route('/api/reviewfromuserexists', methods=['POST'])
@limiter.limit("30 per minute", error_message="BRO, YOU GOTTA CHILL")
def review_from_user_exists():
    required_keys = [ 'placeType'
                    , 'locationX'
                    , 'locationY'
                    ]
    if is_valid_request(request.form, required_keys):
        reviewer_id = uuid.UUID(session['uid'])
        place_id = placesdb.get_place_id(request.form['placeType'],
                request.form['locationX'], request.form['locationY'])
        exists = reviewsdb.review_exists(reviewer_id, place_id)
        return "True" if exists else "False"
    else:
        return "Malformed request"

@app.route('/api/createdplace', methods=['POST'])
@limiter.limit("30 per minute", error_message="BRO, YOU GOTTA CHILL")
def created_place_front_end():
    user_id = uuid.UUID(session['uid'])
    required_keys = [ 'placeType'
                    , 'locationX'
                    , 'locationY'
                    ]
    if is_valid_request(request.form, required_keys):
        place_id = placesdb.get_place_id(request.form['placeType'],
                request.form['locationX'], request.form['locationY'])
        return placesdb.created_place(user_id, place_id)
    else:
        return "Malformed request"

@app.route('/api/getdescription', methods=['POST'])
@limiter.limit("30 per minute", error_message="BRO, YOU GOTTA CHILL")
def get_description_front_end():
    required_keys = [ 'placeType'
                    , 'locationX'
                    , 'locationY'
                    ]
    if is_valid_request(request.form, required_keys):
        place_id = placesdb.get_place_id(request.form['placeType'],
                request.form['locationX'], request.form['locationY'])
        return placesdb.get_place_description(place_id)
    else:
        return "Malformed request"

@app.route('/api/adddescription', methods=['POST'])
@limiter.limit("3 per minute", error_message="BRO, YOU GOTTA CHILL")
def add_description_front_end():
    user_id = uuid.UUID(session['uid'])
    required_keys = [ 'placeType'
                    , 'locationX'
                    , 'locationY'
                    , 'description'
                    ]
    if is_valid_request(request.form, required_keys):
        place_id = placesdb.get_place_id(request.form['placeType'],
                request.form['locationX'], request.form['locationY'])
        description = request.form['description']
        return placesdb.update_place_description(place_id, description)
    else:
        return "Malformed request"

@app.route('/api/getrating', methods=['POST'])
@limiter.limit("30 per minute", error_message="BRO, YOU GOTTA CHILL")
def get_rating_front_end():
    required_keys = [ 'placeType'
                    , 'locationX'
                    , 'locationY'
                    ]
    if is_valid_request(request.form, required_keys):
        place_id = placesdb.get_place_id(request.form['placeType'],
                request.form['locationX'], request.form['locationY'])
        return placesdb.get_place_rating(place_id)
    else:
        return "Malformed request"

# FIXME rename this route, "marionette" literally says nothing about what it
# actually does/returns
@app.route('/api/marionette', methods=['GET', 'POST', 'DELETE', 'PUT'])
@app.route('/api/marionette/<thisisisneverusedwtf>',
        methods=['GET', 'POST', 'DELETE', 'PUT'])
@limiter.limit("10 per minute", error_message="BRO, YOU GOTTA CHILL")
def marionette(thisidisneverusedwtf=None):
    user = session['email']
    user_id = usersdb.get_user_id(user)
    if request.method == "GET":
        ans = []
        for favorite in favoritesdb.get_favorites(user_id):
            fav = {"type": placesdb.get_place_type(favorite[1])
                  , "address": (placesdb.get_place_location_x(favorite[1]),
                      placesdb.get_place_location_y(favorite[1]))
                  , "rating": placesdb.get_place_rating(favorite[1])
            }
            ans.append(fav)
        return json.dumps(ans)
    elif request.method == "POST":
        place = request.get_json()
        # FIXME needs float conversion
        place_id = placesdb.get_place_id(place['type'],
                place['address'][0], place['address'][1])
        return favoritesdb.remove_favorite(user_id, place_id)
    # TODO finish this function
    return "hello"

@app.route('/api/directions/<origin>/<destination>')
@limiter.limit("3 per minute", error_message="BRO, YOU GOTTA CHILL")
def show_directions(origin, destination):
    return render_template("directions.html", origin=origin,
            destination=destination)

@app.route('/api/addreview', methods=['POST'])
@limiter.limit("3 per minute", error_message="BRO, YOU GOTTA CHILL")
def add_review_front_end():
    user = uuid.UUID(session['uid'])
    required_keys = [ 'placeType'
                    , 'locationX'
                    , 'locationY'
                    , 'rating'
                    , 'review'
                    ]
    if is_valid_request(request.form, required_keys):
        try:
            rating = int(request.form['rating'])
            location_x = float(request.form["locationX"])
            location_y = float(request.form["locationY"])
        except ValueError, e:
            return "Malformed request"
        placeid = placesdb.get_place_id(request.form["placeType"],
                location_x, location_y)
        if validate.is_valid_rating(rating):
            return reviewsdb.add_review(placeid, user, rating,
                    request.form["review"])[1]
        else:
            return "Malformed request"
    else:
        return "Malformed request"

@app.route('/api/get', methods=['POST'])
@limiter.limit("10 per minute", error_message="BRO, YOU GOTTA CHILL")
def get():
    try:
        location_x = float(request.form['longitude'])
        location_y = float(request.form['latitude'])
    except ValueError:
        return "Malformed request"
    radius = .014
    return json.dumps(placesdb.get_local_places(location_x, location_y, radius))

@app.route('/api/removeplace', methods=['POST'])
@limiter.limit("10 per minute", error_message="BRO, YOU GOTTA CHILL")
def remove_place_front_end():
    required_keys = [ 'placeType'
                    , 'locationX'
                    , 'locationY'
                    ]
    if is_valid_request(request.form, required_keys):
        place_id = placesdb.get_place_id(request.form['placeType'],
                request.form['locationX'], request.form['locationY'])
    return placesdb.remove_place_by_id(place_id)

@app.route('/api/reportplace', methods=['POST'])
@limiter.limit("3 per minute", error_message="BRO, YOU GOTTA CHILL")
def report_place_front_end():
    user_id = uuid.UUID(session['uid'])
    required_keys = [ 'placeType'
                    , 'locationX'
                    , 'locationY'
                    , 'reason'
                    ]
    if is_valid_request(request.form, required_keys):
        place_id = placesdb.get_place_id(request.form['placeType'],
                request.form['locationX'], request.form['locationY'])
        reason = request.form['reason']
        return placesdb.add_place_report(user_id, place_id, reason)[1]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@limiter.limit("2 per minute", error_message="BRO, YOU GOTTA CHILL")
@redirect_if_not_logged_in("welcome")
def upload():
    if request.method == 'POST' and request.files.has_key('pic'):
        fp = request.files['pic']
        if fp and is_allowed_file_ext(fp.filename):
            try:
                img1 = Image.open(fp.stream)
                img2 = img1.copy()
                img1.thumbnail((256, 256))
                img2.thumbnail((128, 128))
                try:
                    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'],
                        session['uid']))
                except OSError:
                    pass
                img1.save(os.path.join(app.config['UPLOAD_FOLDER'],
                    session['uid'], 'profile256.jpg'))
                img2.save(os.path.join(app.config['UPLOAD_FOLDER'],
                    session['uid'], 'profile128.jpg'))
                flash("Upload successful")
            except IOError, e:
                if app.debug:
                    flash("Invalid image: %s" % e)
                else:
                    flash("Invalid image")
            return redirect(url_for('settings'))
        flash("Upload unsuccessful")
    return redirect(url_for('settings'))

@app.route('/settings/', methods=['GET', 'POST'])
@limiter.limit("10 per minute", error_message="BRO, YOU GOTTA CHILL")
@redirect_if_not_logged_in("welcome")
def settings():
    global TEMP_URL_TIMEOUT_PENDING
    uid = uuid.UUID(session['uid'])
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
            result = dbhelper.auth(AUTH_VERIFY, session, session['email'],
                        request.form['verify_password'])
            if not result[0]:
                flash(result[1])
                return redirect(url_for('settings'))
            else:
                if session['email'] != request.form['new_email']:
                    valid_email = validate.is_valid_email(
                            request.form['new_email'])
                    if valid_email[0]:
                        flash(usersdb.update_user_email(uid,
                            request.form['new_email'])[1])
                    else:
                        flash(valid_email[1])
                valid_phone = validate.is_valid_telephone(
                        request.form['new_phone'])
                if valid_phone[0]:
                    if valid_phone[1] != usersdb.get_user_phone(uid):
                        flash(usersdb.update_user_phone(uid, valid_phone[1])[1])
                else:
                    flash(valid_phone[1])
                if request.form['new_password']:
                    valid_password = validate.is_valid_password(
                            request.form['new_password'])
                    if valid_password[0]:
                        flash(usersdb.update_user_password(uid,
                            request.form['new_password'])[1])
                    else:
                        flash(valid_password[1])
                if request.form['new_firstname'] != \
                  usersdb.get_user_firstname(uid):
                    flash(usersdb.update_user_firstname(uid,
                        request.form['new_firstname'])[1])
                if request.form['new_lastname'] != \
                        usersdb.get_user_lastname(uid):
                    flash(usersdb.update_user_lastname(uid,
                        request.form['new_lastname'])[1])
                if request.form['new_bio'] != usersdb.get_user_bio(uid):
                    flash(usersdb.update_user_bio(uid,
                              request.form['new_bio'])[1])
        else:
            flash("Malformed request")
    return render_template('settings.html',
                            user_data=usersdb.get_user_data(uid),
                            loggedin=True,
                            temp_url_timeout_pending=TEMP_URL_TIMEOUT_PENDING)

@app.route('/delete_account', methods=['POST'])
@limiter.limit("1 per 10 minutes", error_message="BRO, YOU GOTTA CHILL")
@redirect_if_not_logged_in("welcome")
def delete_account():
    required_keys = ['password']
    if is_valid_request(request.form, required_keys):
        result = dbhelper.auth(AUTH_VERIFY, session, session['email'],
                request.form['password'])
        if result[0]:
            uid = uuid.UUID(session['uid'])
            usersdb.remove_user(uid)
        clear_session_login_data(session)
        flash("Account successfully deleted")
        return redirect(url_for('index'))
    else:
        return "Malformed request"

@app.route('/confirm/email/<url_id>', methods=['GET'])
@limiter.limit("2 per minute", error_message="BRO, YOU GOTTA CHILL")
@redirect_if_not_logged_in("welcome")
def confirm_email(url_id=None):
    if url_id:
        url_id = inflate_uuid(url_id)
        if url_id:
            uid = uuid.UUID(session['uid'])
            url_id = uuid.UUID(url_id)
            if tmpurldb.get_temporary_url(url_id,
              uid, TEMP_URL_EMAIL_CONFIRM)[0]:
                usersdb.update_user_email_confirmed(uid, True)
                tmpurldb.remove_temporary_url(url_id)
                return redirect(url_for('settings'))
    return redirect(url_for('index'))

@app.route('/confirm/send/email', methods=['POST'])
@limiter.limit("1 per minute", error_message="BRO, YOU GOTTA CHILL")
@redirect_if_not_logged_in("welcome")
def send_confirm_email():
    uid = uuid.UUID(session['uid'])
    can_send_email = tmpurldb.add_temporary_url(uid, TEMP_URL_EMAIL_CONFIRM)
    if can_send_email[0]:
        url_id = deflate_uuid(str(can_send_email[1]))
        response = emailhelper.send_confirmation_email(session['email'],
                usersdb.get_user_firstname(uid),
                url_id)
        if response:
            flash(response)
            return "OK"
    flash("An error occurred while sending your confirmation email. Please try"
          " again later.")
    return "Fail"

@app.route('/passwordreset/<url_id>', methods=['GET', 'POST'])
@limiter.limit("1 per minute", error_message="BRO, YOU GOTTA CHILL")
def password_reset(url_id=None):
    if url_id:
        if request.method == 'POST':
            required_keys = [ 'resetEmail'
                            , 'new_password'
                            , 'confirm_password'
                            ]
            if is_valid_request(request.form, required_keys):
                email = request.form['resetEmail']
                password = request.form['new_password']
                response = dbhelper.auth(AUTH_PASSRESET, session, email,
                        password, url_id=url_id)
                flash(response[1])
                if response[0]:
                    return redirect(url_for('index'))
            else:
                flash("Malformed request")
        return render_template('password_reset_page.html')
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for('index')), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=APP_PORT)

