import psycopg2, psycopg2.extras
import dbhelper
from constants import *
from utils import *

# TODO favorites should have a primary key
#TODO test favorites
def add_favorite(user_id, place_id):
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("""SELECT * FROM FAVORITES WHERE UserID = %s AND PlacesID = %s
                LIMIT 1""", (user_id, place_id))
        conn.commit()
        exists = c.fetchone()
        print exists
        if not exists:
            c.execute("""INSERT INTO FAVORITES VALUES (%s, %s)""",
                    (user_id, place_id))
            c.execute("""UPDATE Places SET FAVORITES = FAVORITES + 1 WHERE
                    PlaceID = %s""", (place_id,))
            conn.commit()
            return "Location added to My Places"
        else:
            return "Location already in My Places"
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def remove_favorite(user_id, place_id):
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("""DELETE FROM FAVORITES WHERE UserID = %s
            AND PlacesID = %s""", (user_id, place_id))
        conn.commit()
        success = c.rowcount
        if success:
            return "Successfully removed from My Places"
        else:
            return "My Place doesn't exist"
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def in_favorites(user_id, place_id):
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("""SELECT 1 FROM FAVORITES WHERE UserID = %s AND PlacesID = %s
            LIMIT 1""", (user_id, place_id))
        conn.commit()
        exists = c.fetchone()
        # FIXME FIXME FIXME WTF is this?
        if not exists:
            return "False"
        return "True"
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def get_favorites(user_id):
    print "user_id: " + str(user_id)
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("""SELECT * FROM Favorites WHERE UserID = %s""", (user_id,))
        conn.commit()
        return c.fetchall()
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()
