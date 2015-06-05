import psycopg2, psycopg2.extras
from flask import flash, session
from constants import *
import validate
import uuid

def connect():
    try:
        psycopg2.extras.register_uuid()
        return psycopg2.connect("dbname='%s' user='%s'" % (DB_NAME, DB_USER))
    except psycopg2.DatabaseError, e:
        print "Error: %s" % e
        return None

def auth(type, email, password, phone=None, bio=None):
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
                add_user(uuid[1], email, password, phone, bio)
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
                        session['uid'] = str(get_user_id(email))
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

def add_user(uid, email, password, phone, bio):
    conn = connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("INSERT INTO Users VALUES(%s, %s, %s, %s, %s, %s, %s, %s)",
                (uid, uid, email, validate.hash_password(password), phone, '',
                '', bio))
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
    conn = connect()
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
    conn = connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("UPDATE USERS SET Email = %s WHERE ID = %s",
                 (new_email, uid))
        conn.commit()
        session['email'] = new_email
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
        conn.commit()
        return (True, "Successfully updated phone number")
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def get_user_firstname(uid=None, email=None):
    conn = connect()
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
        return results[0]
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def get_user_lastname(uid=None, email=None):
    conn = connect()
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
        return results[0]
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def get_user_bio(uid=None, email=None):
    conn = connect()
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
        return results[0]
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def get_user_email(uid):
    conn = connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("""SELECT Email FROM Users WHERE ID = %s LIMIT 1""",
                        (uid,))
        return c.fetchone()[0]
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def update_user_firstname(uid, new_firstname):
    conn = connect()
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
    conn = connect()
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
    conn = connect()
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
    conn = connect()
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
    conn = connect()
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
    conn = connect()
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
    conn = connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("""SELECT Phone FROM Users WHERE ID = %s LIMIT 1""",
                        (uid,))
        return c.fetchone()[0]
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def get_user_id(email):
    conn = connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("""SELECT UserID FROM Users WHERE Email = %s LIMIT 1""",
                        (email,))
        return c.fetchone()[0]
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def get_user_data(_uid):
    # TODO condense this to a single query... lmao
    user_email = get_user_email(_uid)
    user_phone = get_user_phone(_uid)
    user_firstname = get_user_firstname(_uid)
    user_lastname = get_user_lastname(_uid)
    user_bio = get_user_bio(_uid)
    user_email_confirmed = get_user_email_confirmed(_uid)
    user_phone_confirmed = get_user_phone_confirmed(_uid)
    user_data = {
        'uid' : str(_uid),
        'email' : user_email,
        'phone' : user_phone,
        'first_name' : user_firstname,
        'last_name' : user_lastname,
        'bio' : user_bio if user_bio else "",
        'email_confirmed' : user_email_confirmed,
        'phone_confirmed' : user_phone_confirmed,
    }
    return user_data

def get_user_disabled(uid):
    conn = connect()
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
    conn = connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("SELECT EmailConfirmed FROM USERS WHERE ID = %s LIMIT 1",
                 (uid,))
        return c.fetchone()[0]
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def get_user_phone_confirmed(uid):
    conn = connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("SELECT PhoneConfirmed FROM USERS WHERE ID = %s LIMIT 1",
                 (uid,))
        return c.fetchone()[0]
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
        exists = c.fetchone()
        #if exists == ():
        if True:
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
            "ID": str(place[0]),
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
        c.execute("""SELECT 1 FROM Users WHERE Email = %s LIMIT 1""", (email,))
        return c.fetchone()
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def uid_exists(uid):
    conn = connect()
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
