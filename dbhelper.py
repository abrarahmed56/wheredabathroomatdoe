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
                c.execute("INSERT INTO Users VALUES(%s, %s, %s, %s)",
                          (uuid[1], email, validate.generate_password_hash(password),
                           phone))
                conn.commit()
                return "Registration successful"
            else:
                return "A user with that email already exists"
        elif type == AUTH_LOGIN:
            print c.execute("""SELECT Password FROM Users WHERE Email = %s""",
                            (email,))
            results = c.fetchall()
            success = False
            if results != []:
                if validate.check_password(results[0][0], password):
                    session['email'] = email
                    success = True
                    return "Login successful"
            if not success:
                return "Incorrect login information"
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def add_place(name, location_x, location_y, finder):
    global ID_PLACE
    conn = connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        #remember to change the first 0 into a random int
        c.execute("SELECT 1 FROM Places WHERE Name=%s AND LocationX=%s AND LocationY=%s", (name, location_x, location_y))
        exists = c.fetchall()
        if exists == []:
            uuid = generate_id(ID_PLACE)
            if not uuid[0]:
                return "UUID error"
            c.execute("INSERT INTO Places VALUES(%s, %s, %s, %s, 0, %s)",
                      (uuid[1], name, location_x, location_y, finder))
            conn.commit()
            return "Location added to map"
        else:
            return "Location already exists"
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def remove_place(name, location_x, location_y):
    conn = connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("""DELETE FROM Places WHERE Name = %s AND LocationX = %s AND
                  LocationY = %s""", (name, location_x, location_y))
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
        return (False, "Database Error")
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
