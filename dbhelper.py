import psycopg2, psycopg2.extras
from flask import flash, session
from constants import *
from utils import *
import users_dbhelper as userdb
import places_dbhelper as placedb
import temporaryurls_dbhelper as tmpurldb
import validate
import uuid

def connect():
    try:
        psycopg2.extras.register_uuid()
        return psycopg2.connect("dbname='%s' user='%s'" % (DB_NAME, DB_USER))
    except psycopg2.DatabaseError, e:
        print "Error: %s" % e
        return None

def auth(type, _session, email, password, phone=None, bio=None, url_id=None):
    global ID_USER, TEMP_URL_PASSWORD_RESET
    conn = connect()
    if conn == None:
        return (False, "Database Error")
    c = conn.cursor()
    try:
        if type == AUTH_REGISTER:
            valid_email = validate.is_valid_email(email, check_db=False)
            if not valid_email[0]:
                return (False, valid_email[1])
            valid_password = validate.is_valid_password(password)
            if not valid_password[0]:
                return (False, valid_password[1])
            valid_phone = validate.is_valid_telephone(phone)
            if not valid_phone[0]:
                return (False, valid_phone[1])
            if not userdb.email_exists(email):
                uid = generate_id(ID_USER)
                if not uid[0]:
                    return (False, "UUID error")
                userdb.add_user(uid[1], email, password, phone, bio)
                return (True, "Registration successful")
            else:
                return (False, "A user with that email already exists")
        elif type == AUTH_LOGIN or type == AUTH_VERIFY:
            stored_pass = userdb.get_user_password(email=email)
            success = False
            if stored_pass:
                if validate.check_password(stored_pass, password):
                    uid = userdb.get_user_id(email)
                    if userdb.get_user_disabled(uid):
                        clear_session_login_data(_session)
                        return (False, "This account has been disabled")
                    if type == AUTH_LOGIN:
                        _session['email'] = email
                        _session['uid'] = str(uid)
                        success = True
                        return (True, "Login successful")
                    elif type == AUTH_VERIFY:
                        success = True
                        return (True, "Verification successful")
            if not success:
                return (False, "Incorrect credentials")
        elif type == AUTH_PASSRESET:
            if userdb.email_exists(email):
                uid = userdb.get_user_id(email)
                if tmpurldb.get_temporary_url(url_id, uid, TEMP_URL_PASSWORD_RESET)[0]:
                    userdb.update_user_password(uid, password)
                    return (True, "Password successfully reset")
                else:
                    return (False, "Invalid url")
            else:
                return (False, "User not found")

    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn: conn.close()

def generate_id(datatype):
    global ID_USER, ID_PLACE, ID_REVIEW, ID_TEMPORARY_URL,\
           ID_REPORTS_USERS, ID_REPORTS_PLACES
    query = ""
    if datatype == ID_USER:
        query = "SELECT 1 FROM Users WHERE ID = %s LIMIT 1"
    elif datatype == ID_PLACE:
        query = "SELECT 1 FROM Places WHERE ID = %s LIMIT 1"
    elif datatype == ID_REVIEW:
        query = "SELECT 1 FROM Reviews WHERE ID = %s LIMIT 1"
    elif datatype == ID_TEMPORARY_URL:
        query = "SELECT 1 FROM TemporaryUrls WHERE ID = %s LIMIT 1"
    elif datatype == ID_REPORTS_USERS:
        query = "SELECT 1 FROM ReportsUsers WHERE ID = %s LIMIT 1"
    elif datatype == ID_REPORTS_PLACES:
        query = "SELECT 1 FROM ReportsPlaces WHERE ID = %s LIMIT 1"
    success = False
    u = uuid.uuid4()
    conn = connect()
    if conn == None:
        return (False, "Database Error when Generating UUID")
    c = conn.cursor()
    try:
        while not success:
            c.execute(query, (u,))
            if c.fetchone() == None:
                success = True
            else:
                u = uuid.uuid4()
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()
    return (True, u)
