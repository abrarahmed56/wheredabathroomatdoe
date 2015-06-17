import psycopg2, psycopg2.extras
from flask import url_for
import dbhelper
import validate
import uuid
import os.path
import qrcode
import shutil
from flask import session
from constants import *
from utils import *
import temporaryurls_dbhelper as tmpurldb

def add_user(uid, email, password, phone, bio):
    global UPLOAD_FOLDER, WEBSITE_URL_BASE
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("INSERT INTO Users VALUES(%s, %s, %s, %s, %s, %s, %s, %s)",
                (uid, uid, email, validate.hash_password(password), phone, '',
                '', bio))
        conn.commit()
        try:
            os.makedirs(os.path.join(UPLOAD_FOLDER, str(uid)))
        except OSError:
            pass
        try:
            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=12,
                border=4,
            )
            qr_data = WEBSITE_URL_BASE + url_for('profile_with_id', 
                    userid=deflate_uuid(str(uid)))
            qr.add_data(qr_data)
            qr.make(fit=True)
            img1 = qr.make_image()
            img2 = img1.copy()
            img1.thumbnail((256, 256))
            img2.thumbnail((128, 128))
            img1.save(get_user_profile_pic_url(uid, 256).lstrip('/'))
            img2.save(get_user_profile_pic_url(uid, 128).lstrip('/'))
        except IOError, e:
            print "Error %s: " % e
    except psycopg2.DatabaseError, e:
        print "Error %s: " % e
    finally:
        if conn:
            conn.close()

def remove_user(uid):
    global UPLOAD_FOLDER
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("DELETE FROM Users WHERE UserID = %s", (uid,))
        conn.commit()
        # Remove files uploaded by the user
        try:
            shutil.rmtree(os.path.join(UPLOAD_FOLDER, str(uid)))
        except OSError:
            pass
    except psycopg2.DatabaseError, e:
        print "Error %s: " % e
    finally:
        if conn:
            conn.close()

def get_user_password(uid=None, email=None):
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        results = ()
        if uid:
            c.execute("""SELECT Password FROM Users WHERE ID = %s LIMIT 1""",
                            (uid,))
            results = c.fetchone()
        elif email:
            c.execute("""SELECT Password FROM Users WHERE Email = %s LIMIT 1""",
                            (email,))
            results = c.fetchone()
        return results[0] if results else None
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def update_user_password(uid, new_password, verify_old_password=None):
    # NOTE: Make sure password is validated before calling this method
    # Verification of the old password can be skipped by setting
    # verify_old_password to None
    if verify_old_password:
        old_password = get_user_password(uid=uid)
        if old_password:
            if not validate.check_password(old_password, verify_old_password):
                return (False, "Invalid verification credentials")
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("UPDATE USERS SET Password = %s WHERE ID = %s",
                 (validate.hash_password(new_password), uid))
        conn.commit()
        return (True, "Successfully updated password")
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def update_user_email(uid, new_email, verify_password=None):
    # NOTE: Make sure email is validated before calling this method
    # Verification of the old password can be skipped by setting
    # verify_password to None
    if verify_password:
        old_password = get_user_password(uid=uid)
        if old_password:
            if not validate.check_password(old_password, verify_password):
                return (False, "Invalid verification credentials")
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("UPDATE USERS SET Email = %s WHERE ID = %s",
                 (new_email, uid))
        conn.commit()
        session['email'] = new_email
        update_user_email_confirmed(uid, False)
        return (True, "Successfully updated email")
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def update_user_phone(uid, new_phone, verify_password=None):
    # NOTE: Make sure phone is validated before calling this method
    # Verification of the old password can be skipped by setting
    # verify_password to None
    if verify_password:
        old_password = get_user_password(uid=uid)
        if old_password:
            if not validate.check_password(old_password, verify_password):
                return (False, "Invalid verification credentials")
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("UPDATE USERS SET Phone = %s WHERE ID = %s",
                 (new_phone, uid))
        conn.commit()
        return (True, "Successfully updated phone number")
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def get_user_firstname(uid=None, email=None):
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        results = ()
        if uid:
            c.execute("""SELECT FirstName FROM Users WHERE ID = %s LIMIT 1""",
                            (uid,))
            results = c.fetchone()
        elif email:
            c.execute("""SELECT FirstName FROM Users WHERE Email = %s LIMIT 1""",
                            (email,))
            results = c.fetchone()
        if results[0]:
            return results[0]
        else:
            return 'Anonymous'
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def get_user_lastname(uid=None, email=None):
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        results = ()
        if uid:
            c.execute("""SELECT LastName FROM Users WHERE ID = %s LIMIT 1""",
                            (uid,))
            results = c.fetchone()
        elif email:
            c.execute("""SELECT LastName FROM Users WHERE Email = %s LIMIT 1""",
                            (email,))
            results = c.fetchone()
        if results[0]:
            return results[0]
        else:
            return ''
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def get_user_bio(uid=None, email=None):
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        results = ()
        if uid:
            c.execute("""SELECT Bio FROM Users WHERE ID = %s LIMIT 1""",
                            (uid,))
            results = c.fetchone()
        elif email:
            c.execute("""SELECT Bio FROM Users WHERE Email = %s LIMIT 1""",
                            (email,))
            results = c.fetchone()
        return results[0] if results else None
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def get_user_email(uid):
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("""SELECT Email FROM Users WHERE ID = %s LIMIT 1""",
                        (uid,))
        result = c.fetchone()
        return result[0] if result else None
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def get_user_profile_pic_url(uid, size):
    return "/static/uploads/" + str(uid) + "/profile" + str(size) + ".jpg"

def get_user_profile_url(uid):
    return "/profile/" + deflate_uuid(str(uid))

def update_user_firstname(uid, new_firstname):
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("UPDATE USERS SET FirstName = %s WHERE ID = %s",
                 (new_firstname, uid))
        conn.commit()
        return (True, "Successfully updated user first name")
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def update_user_lastname(uid, new_lastname):
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("UPDATE USERS SET LastName = %s WHERE ID = %s",
                 (new_lastname, uid))
        conn.commit()
        return (True, "Successfully updated user last name")
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def update_user_bio(uid, new_bio):
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("UPDATE USERS SET Bio = %s WHERE ID = %s",
                 (new_bio, uid))
        conn.commit()
        return (True, "Successfully updated user bio")
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def update_user_disabled(uid, disabled):
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("UPDATE USERS SET Disabled = %s WHERE ID = %s",
                 (disabled, uid))
        conn.commit()
        return (True, "Successfully updated user disabled flag")
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def update_user_email_confirmed(uid, confirmed):
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("UPDATE USERS SET EmailConfirmed = %s WHERE ID = %s",
                 (confirmed, uid))
        conn.commit()
        return (True, "Successfully updated user email confirmed flag")
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def update_user_phone_confirmed(uid, confirmed):
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("UPDATE USERS SET PhoneConfirmed = %s WHERE ID = %s",
                 (confirmed, uid))
        conn.commit()
        return (True, "Successfully updated user phone confirmed flag")
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def get_user_phone(uid):
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("""SELECT Phone FROM Users WHERE ID = %s LIMIT 1""",
                        (uid,))
        result = c.fetchone()
        return result[0] if result else None
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def get_user_id(email):
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("""SELECT UserID FROM Users WHERE Email = %s LIMIT 1""",
                        (email,))
        result = c.fetchone()
        return result[0] if result else None
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def get_user_data(_uid):
    # TODO condense this to a single query... lmao
    uid_str = str(_uid)
    user_email = get_user_email(_uid)
    user_phone = get_user_phone(_uid)
    user_firstname = get_user_firstname(_uid)
    user_lastname = get_user_lastname(_uid)
    user_bio = get_user_bio(_uid)
    user_email_confirmed = get_user_email_confirmed(_uid)
    user_email_confirm_timeout_pending = tmpurldb.get_temporary_url_timeout_pending(
                                            _uid,
                                            TEMP_URL_EMAIL_CONFIRM)[0]
    user_phone_confirmed = get_user_phone_confirmed(_uid)
    user_profile_pic = get_user_profile_pic_url(_uid, 256)
    user_can_be_reported = True
    try:
        user_can_be_reported = can_user_be_reported(uuid.UUID(session['uid']),
                                                    _uid)
    except ValueError, e:
        user_can_be_reported = False
    user_data = {
        'uid' : uid_str,
        'uid-deflated' : deflate_uuid(uid_str),
        'email' : user_email,
        'phone' : user_phone,
        'first_name' : user_firstname,
        'last_name' : user_lastname,
        'bio' : user_bio if user_bio else "",
        'email_confirmed' : user_email_confirmed,
        'email_confirm_timeout_pending' : user_email_confirm_timeout_pending,
        'phone_confirmed' : user_phone_confirmed,
        'profile_pic' : user_profile_pic,
        'user_can_be_reported' : user_can_be_reported,
    }
    return user_data

def get_user_disabled(uid):
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("SELECT Disabled FROM USERS WHERE ID = %s LIMIT 1",
                 (uid,))
        return c.fetchone()[0]
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def get_user_email_confirmed(uid):
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("SELECT EmailConfirmed FROM USERS WHERE ID = %s LIMIT 1",
                 (uid,))
        result = c.fetchone()
        return result[0] if result else None
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def get_user_phone_confirmed(uid):
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("SELECT PhoneConfirmed FROM USERS WHERE ID = %s LIMIT 1",
                 (uid,))
        result = c.fetchone()
        return result[0] if result else None
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def email_exists(email):
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("""SELECT 1 FROM Users WHERE Email = %s LIMIT 1""", (email,))
        return c.fetchone()
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def uid_exists(uid):
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("""SELECT 1 FROM Users WHERE UserId = %s LIMIT 1""", (uid,))
        return c.fetchone()
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def add_user_report(reporter_id, reported_id, reason):
    global ID_REPORTS_USERS, USER_REPORT_LIMIT
    ruid = dbhelper.generate_id(ID_REPORTS_USERS)
    if not ruid[0]:
        return (False, "UUID error")
    conn = connect()
    if conn == None:
        return (False, "Database Error")
    c = conn.cursor()
    try:
        c.execute("""INSERT INTO ReportsUsers (ID, ReportID, ReporterId, ReportedId,
                Reason)  VALUES (%s, %s, %s, %s, %s)""",
                (ruid[1], ruid[1], reporter_id, reported_id, reason))
        conn.commit()
        if get_num_reports_for_user(reported_id) >= USER_REPORT_LIMIT:
            update_user_disabled(reported_id, True)
        return (True, "User report successful")
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def remove_user_report(reporter_id, reported_id):
    conn = connect()
    if conn == None:
        return (False, "Database Error")
    c = conn.cursor()
    try:
        c.execute("""REMOVE FROM ReportsUsers WHERE ReporterId = %s AND
        ReportedId = %s
                  """, (reporter_id, reported_id))
        conn.commit()
        return (True, "User report removal successful")
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def is_user_reported_by(reporter_id, reported_id):
    conn = connect()
    if conn == None:
        return (False, "Database Error")
    c = conn.cursor()
    try:
        c.execute("""SELECT 1 FROM ReportsUsers WHERE ReporterId = %s AND
        ReportedId = %s LIMIT 1
                  """, (reporter_id, reported_id))
        return c.fetchone()
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def can_user_be_reported(reporter_id, reported_id):
    return reporter_id != reported_id and\
            not is_user_reported_by(reporter_id, reported_id)

def get_num_reports_for_user(reported_id):
    conn = dbhelper.connect()
    if conn == None:
        return (False, "Database Error")
    c = conn.cursor()
    try:
        c.execute("""SELECT 1 FROM ReportsUsers WHERE ReportedId = %s""",
                (reported_id,))
        return len(c.fetchall())
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

