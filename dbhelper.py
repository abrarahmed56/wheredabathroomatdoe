import psycopg2
import sys
from flask import flash, session
from constants import *
import validate

def auth(type, email, password, phone=None):
    conn = None
    try:
        conn = psycopg2.connect("dbname='%s' user='%s'" % (DB_NAME, DB_USER))
        c = conn.cursor()
        if type=="register":
            c.execute("SELECT 1 FROM Users WHERE Email = %s", (email,))
            if c.fetchall() == []:
                c.execute("INSERT INTO Users VALUES(%s, %s, %s)",
                          (email, validate.generate_password_hash(password),
                           phone))
                conn.commit()
                return "Registration successful"
            else:
                return "Username is taken"
        elif type=="login":
            print c.execute("""SELECT * FROM Users WHERE Email = %s""",
                            (email,))
            results = c.fetchall()
            success = False
            if results != []:
                if validate.check_password(results[0][1], password):
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

def addPlace(name, locationX, locationY, finder):
    conn = None
    try:
        conn = psycopg2.connect("dbname='%s' user='%s'" % (DB_NAME, DB_USER))
        c = conn.cursor()
        #remember to change the first 0 into a random int
        c.execute("SELECT * FROM Places WHERE Name=%s AND LocationX=%s AND LocationY=%s", (name, locationX, locationY))
        exists = c.fetchall()
        if exists == []:
            c.execute("INSERT INTO Places VALUES(%s, %s, %s, %s, 0, %s)",
                  (0, name, locationX, locationY, finder))
            conn.commit()
            return "Location added to map"
        else:
            return "Location already exists"
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def removePlace(name, locationX, locationY):
    conn = None
    try:
        conn = psycopg2.connect("dbname='%s' user='%s'" % (DB_NAME, DB_USER))
        c = conn.cursor()
        c.execute("""DELETE FROM Places WHERE Name = %s AND LocationX = %s AND
                  LocationY = %s""", (name, locationX, locationY))
        conn.commit()
        return "Location removed from map"
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def getPlaces():
    conn = None
    try:
        conn = psycopg2.connect("dbname='%s' user='%s'" % (DB_NAME, DB_USER))
        c = conn.cursor()
        c.execute("SELECT * FROM PLACES")
        conn.commit()
        return dictionarify(c.fetchall())
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def dictionarify(placesList):
    ans = []
    for place in placesList:
        placeDict = {
            "ID": place[0],
            "type": place[1],
            "position": [place[2], place[3]],
            "finder": place[4]
        }
        ans.append(placeDict)
    return ans

def getLocalPlaces(locationX, locationY, radius):
    conn = None
    try:
        conn = psycopg2.connect("dbname='%s' user='%s'" % (DB_NAME, DB_USER))
        c = conn.cursor()
        c.execute("""SELECT * FROM PLACES WHERE abs(LocationX-%s) <= %s AND
        abs(LocationY-%s) <= %s""", (locationX, radius, locationY, radius))
        #c.execute("""SELECT * FROM PLACES WHERE abs(LocationX-%s) <= 1 AND abs(LocationY-%s) <= 1""", ('3', '3'))
        conn.commit()
        return dictionarify(c.fetchall())
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def emailExists(email):
    conn = None
    try:
        conn = psycopg2.connect("dbname='%s' user='%s'" % (DB_NAME, DB_USER))
        c = conn.cursor()
        c.execute("""SELECT 1 FROM Users WHERE Email = %s""", (email,))
        conn.commit()
        return len(c.fetchall()) > 0
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()
