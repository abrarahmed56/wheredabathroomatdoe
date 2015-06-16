import psycopg2, psycopg2.extras
import dbhelper
from constants import *
from utils import *

def expire_temporary_urls():
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("""DELETE FROM TemporaryUrls WHERE CreationTime < NOW() -
                ExpiryTime""")
        conn.commit()
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def add_temporary_url(uid, url_type):
    global TEMP_URL_EXPIRY_TIME
    expire_temporary_urls()
    if get_temporary_url_timeout_pending(uid, url_type)[0]:
        return (False, "The temporary url timeout has not expired")
    uuid = dbhelper.generate_id(ID_USER)
    if not uuid[0]:
        return (False, "UUID error")
    conn = dbhelper.connect()
    if conn == None:
        return (False, "Database Error")
    c = conn.cursor()
    try:
        c.execute("""INSERT INTO TemporaryUrls VALUES(%s, %s, NOW(), INTERVAL
                  %s, %s, %s)""",
                  (uuid[1], uuid[1], TEMP_URL_EXPIRY_TIME, url_type, uid))
        conn.commit()
        return (True, uuid[1])
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def get_temporary_url(uuid, uid, url_type):
    conn = dbhelper.connect()
    if conn == None:
        return (False, "Database Error")
    c = conn.cursor()
    try:
        c.execute("""SELECT 1 FROM TemporaryUrls WHERE UrlID = %s AND UserID =
                  %s AND UrlType = %s AND CreationTime >= NOW() - ExpiryTime
                  LIMIT 1""", (uuid, uid, url_type))
        if c.fetchone():
            return (True, "Valid temporary url")
        else:
            return (False, "Invalid temporary url")
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def remove_temporary_url(uuid):
    conn = dbhelper.connect()
    if conn == None:
        return (False, "Database Error")
    c = conn.cursor()
    try:
        c.execute("""DELETE FROM TemporaryUrls WHERE UrlID = %s""", (uuid,))
        conn.commit()
        return (True, "Successfully deleted temporary url")
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def get_temporary_url_timeout_pending(uid, url_type):
    # Returns whether there is a timeout on creating a temporary url because one
    # is still pending
    global TEMP_URL_TIMEOUT_PENDING
    conn = dbhelper.connect()
    if conn == None:
        return (False, "Database Error")
    c = conn.cursor()
    try:
        c.execute("""SELECT 1 FROM TemporaryUrls WHERE UserID =
                  %s AND UrlType = %s AND CreationTime >= NOW() - INTERVAL %s
                  LIMIT 1""", (uid, url_type, TEMP_URL_TIMEOUT_PENDING))
        if c.fetchone():
            return (True, "Temporary url pending")
        else:
            return (False, "No temporary url pending")
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()
