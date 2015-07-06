import psycopg2, psycopg2.extras
import dbhelper
from constants import *
from utils import *

# TODO favorites should have a primary key
def add_favorite(user_id, place_id, conn=None):
    persist_conn = True
    if not conn:
        conn = dbhelper.connect()
        persist_conn = False
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("""SELECT * FROM FAVORITES WHERE UserID = %s AND PlacesID = %s
                LIMIT 1""", (user_id, place_id))
        conn.commit()
        exists = c.fetchone()
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
        if conn and not persist_conn:
            conn.close()

def remove_favorite(user_id, place_id, conn=None):
    persist_conn = True
    if not conn:
        conn = dbhelper.connect()
        persist_conn = False
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
        if conn and not persist_conn:
            conn.close()

def in_favorites(user_id, place_id, conn=None):
    persist_conn = True
    if not conn:
        conn = dbhelper.connect()
        persist_conn = False
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("""SELECT 1 FROM FAVORITES WHERE UserID = %s AND PlacesID = %s
            LIMIT 1""", (user_id, place_id))
        conn.commit()
        exists = c.fetchone()
        if exists:
            return True
        else:
            return False
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn and not persist_conn:
            conn.close()

def get_favorites(user_id, conn=None):
    persist_conn = True
    if not conn:
        conn = dbhelper.connect()
        persist_conn = False
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
        if conn and not persist_conn:
            conn.close()
