import psycopg2
import sys
from flask import flash, session

def auth(type, email, password, phone=None):
    conn = None
    try:
        conn = psycopg2.connect("dbname='users' user='softdev'")
        c = conn.cursor()
        c.execute("SELECT * FROM Users")
        if type=="register":
            c.execute("SELECT 1 FROM Users WHERE Email = '" + email + "'")
            if c.fetchall() == []:
                c.execute("INSERT INTO Users VALUES('" + email + "', '" + password + "', '" + phone + "')")
                conn.commit()
                print "Registration successful"
                flash("Registration successful")
            else:
                print "Username is take"
                flash("Username is take")
        elif type=="login":
            print c.execute("SELECT * FROM Users WHERE Email = '" + email + "' AND Password = '" + password + "'")
            if c.fetchall() == []:
                print "Incorrect login information"
                flash("Incorrect login information")
            else:
                print "Login successful"
                flash("Login successful")
                session['email'] = email
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def addPlace(name, locationX, locationY):
    conn = None
    try:
        conn = psycopg2.connect("dbname='users' user='softdev'")
        c = conn.cursor()
        c.execute("INSERT INTO Places VALUES('" + name + "', '" + locationX + "', '" + locationY + "', 0)")
        conn.commit()
        print "Location added to map"
        flash("Location added to map")
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def removePlace(name, locationX, locationY):
    conn = None
    try:
        conn = psycopg2.connect("dbname='users' user='softdev'")
        c = conn.cursor()
        c.execute("DELETE FROM Places WHERE Name = '" + name + "' AND LocationX = '" + locationX + "' AND LocationY = '" + locationY + "'")
        conn.commit()
        print "Location removed from map"
        flash("Location removed from map")
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def getPlaces():
    conn = None
    try:
        conn = psycopg2.connect("dbname='users' user='softdev'")
        c = conn.curson()
        c.execute("SELECT * FROM PLACES")
        return c.fetchall()
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()
