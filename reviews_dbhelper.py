import psycopg2, psycopg2.extras
import dbhelper
from constants import *
from utils import *

def add_review(placeID, reviewer, rating, review):
    global ID_REVIEW
    conn = dbhelper.connect()
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
        return (True, ret_str)
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def get_reviews(placeID):
    conn = dbhelper.connect()
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
        if conn:
            conn.close()
