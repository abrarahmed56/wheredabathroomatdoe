import psycopg2, psycopg2.extras
import dbhelper
from constants import *
from utils import *
from places_dbhelper import calc_rating

def add_review(placeID, reviewer, rating, review, conn=None):
    global ID_REVIEW
    persist_conn = True
    if not conn:
        conn = dbhelper.connect()
        persist_conn = False
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        uuid = dbhelper.generate_id(ID_REVIEW)
        if not uuid[0]:
            return (False, uuid[1])
        c.execute("""SELECT * FROM Reviews WHERE Reviewer=%s AND PlacesID=%s
            LIMIT 1""", (reviewer, placeID))
        conn.commit()
        exists = c.fetchone()
        ret_str = ""
        if not exists:
            c.execute("INSERT INTO Reviews VALUES(%s, %s, %s, %s, %s, %s)",
                      (uuid[1], uuid[1], placeID, reviewer, rating, review))
            ret_str = "Successfully added review"
        else:
            c.execute("""UPDATE Reviews SET Rating=%s, Review=%s WHERE
                Reviewer=%s AND PlacesID=%s""",
                (rating, review, reviewer, placeID))
            ret_str = "Successfully updated review"
        conn.commit()
        calc_rating(placeID)
        return (True, ret_str)
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn and not persist_conn:
            conn.close()

def get_reviews(placeID, conn=None):
    persist_conn = True
    if not conn:
        conn = dbhelper.connect()
        persist_conn = False
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM Reviews WHERE PlacesID=%s", (placeID,))
        conn.commit()
        return c.fetchall()
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn and not persist_conn:
            conn.close()

def review_exists(reviewer_id, place_id, conn=None):
    persist_conn = True
    if not conn:
        conn = dbhelper.connect()
        persist_conn = False
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM Reviews WHERE Reviewer=%s AND PlacesID=%s LIMIT 1", (reviewer_id, place_id))
        conn.commit()
        return True if c.fetchone() else False
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn and not persist_conn:
            conn.close()
