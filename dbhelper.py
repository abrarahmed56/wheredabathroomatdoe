import psycopg2, psycopg2.extras
from flask import flash, session
from constants import *
import validate
import uuid

def connect():
    try:
        return psycopg2.connect("dbname='%s' user='%s'" % (DB_NAME, DB_USER))
    except psycopg2.DatabaseError, e:
        print "Error: %s" % e
        return None

def auth(type, email, password, phone=None):
    global ID_USER
    conn = connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        if type == AUTH_REGISTER:
            valid_email = validate.is_valid_email(email, check_db=False)
            if not valid_email[0]:
                return valid_email[1]
            valid_password = validate.is_valid_password(password)
            if not valid_password[0]:
                return valid_password[1]
            valid_phone = validate.is_valid_telephone(phone)
            if not valid_phone[0]:
                return valid_phone[1]
            if not email_exists(email):
                uuid = generate_id(ID_USER)
                if not uuid[0]:
                    return "UUID error"
                add_user(uuid[1], email, password, phone)
                return "Registration successful"
            else:
                return "A user with that email already exists"
        elif type == AUTH_LOGIN or type == AUTH_VERIFY:
            stored_pass = get_user_password(email=email)
            success = False
            if stored_pass:
                if validate.check_password(stored_pass, password):
                    if type == AUTH_LOGIN:
                        session['email'] = email
                        success = True
                        return "Login successful"
                    elif type == AUTH_VERIFY:
                        success = True
                        return "Verification successful"
            if not success:
                return "Incorrect credentials"
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def add_user(uid, email, password, phone):
    conn = connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("INSERT INTO Users VALUES(%s, %s, %s, %s)",
                (uid, email, validate.hash_password(password), phone))
        conn.commit()
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def get_user_password(uid=None, email=None):
    conn = connect()
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
        return results[0]
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
    conn = connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("UPDATE USERS SET Password = %s WHERE ID = %s",
                 (validate.hash_password(new_password), uid))
        c.commit()
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
    conn = connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("UPDATE USERS SET Email = %s WHERE ID = %s",
                 (new_email, uid))
        c.commit()
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
    conn = connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("UPDATE USERS SET Phone = %s WHERE ID = %s",
                 (new_phone, uid))
        c.commit()
        return (True, "Successfully updated phone number")
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def add_place(place_type, location_x, location_y, finder):
    global ID_PLACE
    conn = connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("SELECT 1 FROM Places WHERE PlaceType=%s AND LocationX=%s AND LocationY=%s LIMIT 1",
                 (place_type, location_x, location_y))
        exists = c.fetchall()
        if exists == []:
            uuid = generate_id(ID_PLACE)
            if not uuid[0]:
                return uuid[1]
            c.execute("INSERT INTO Places VALUES(%s, %s, %s, %s, 0, %s)",
                      (uuid[1], place_type, location_x, location_y, finder))
            conn.commit()
            return "Location added to map"
        else:
            return "Location already exists"
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def remove_place(place_type, location_x, location_y):
    conn = connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("""DELETE FROM Places WHERE PlaceType = %s AND LocationX = %s AND
                  LocationY = %s LIMIT 1""", (place_type, location_x, location_y))
        conn.commit()
        return "Location removed from map"
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def get_places():
    conn = connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM PLACES")
        conn.commit()
        return dictionarify(c.fetchall())
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def dictionarify(places_list):
    ans = []
    for place in places_list:
        place_dict = {
            "ID": place[0],
            "type": place[1],
            "position": [place[2], place[3]],
            "finder": place[4]
        }
        ans.append(place_dict)
    return ans

def get_local_places(location_x, location_y, radius):
    conn = connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("""SELECT * FROM PLACES WHERE abs(LocationX-%s) <= %s AND
        abs(LocationY-%s) <= %s""", (location_x, radius, location_y, radius))
        #c.execute("""SELECT * FROM PLACES WHERE abs(LocationX-%s) <= 1 AND abs(LocationY-%s) <= 1""", ('3', '3'))
        conn.commit()
        return dictionarify(c.fetchall())
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def email_exists(email):
    conn = connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("""SELECT 1 FROM Users WHERE Email = %s""", (email,))
        conn.commit()
        return len(c.fetchall()) > 0
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def generate_id(datatype):
    global ID_USER, ID_PLACE, ID_REVIEW
    query = ""
    if datatype == ID_USER:
        query = "SELECT 1 FROM USERS WHERE ID = %s"
    elif datatype == ID_PLACE:
        query = "SELECT 1 FROM PLACE WHERE ID = %s"
    elif datatype == ID_REVIEW:
        query = "SELECT 1 FROM REVIEW WHERE ID = %s"
    success = False
    psycopg2.extras.register_uuid()
    u = uuid.uuid4()
    conn = connect()
    if conn == None:
        return (False, "Database Error when Generating UUID")
    c = conn.cursor()
    try:
        while not success:
            c.execute(query, (u,))
            conn.commit()
            if len(c.fetchall()) == 0:
                success = True
            else:
                u = uuid.uuid4()
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()
    return (True, u)

def add_review(placeID, user, rating, review):
    conn = connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        uuid = generate_id(ID_REVIEW)
        if not uuid[0]:
            return uuid[1]
        c.execute("INSERT INTO Reviews VALUES(%s, %s, %s, %s)",
                      (uuid[1], user, rating, review))
        conn.commit()
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()
