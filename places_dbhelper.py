import psycopg2, psycopg2.extras
import dbhelper
import validate
import uuid
import users_dbhelper as usersdb
from constants import *
from utils import *

def add_place(place_type, location_x, location_y, finder):
    global ID_PLACE
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("""SELECT 1 FROM Places WHERE PlaceType=%s AND LocationX=%s AND
                LocationY=%s LIMIT 1""",
                 (place_type, location_x, location_y))
        exists = c.fetchone()
        if not exists:
            puid = dbhelper.generate_id(ID_PLACE)
            if not puid[0]:
                return puid[1]
            c.execute("INSERT INTO Places VALUES(%s, %s, %s, %s, %s, 0, %s)",
                      (puid[1], puid[1], place_type, location_x, location_y,
                          usersdb.get_user_id(finder)))
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
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("""DELETE FROM Places WHERE PlaceType = %s AND LocationX = %s AND LocationY = %s""", (place_type, location_x, location_y))
        conn.commit()
        return "Location removed from map"
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def remove_place_by_id(place_id):
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("""DELETE FROM Places WHERE PlaceId = %s""", (place_id,))
        conn.commit()
        return "Location removed"
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def get_place_finder(place_id):
    global ID_PLACE
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("SELECT Finder FROM Places WHERE PlaceId=%s LIMIT 1",
                 (place_id,))
        results = c.fetchone()
        return results[0] if results else None
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def get_places():
    conn = dbhelper.connect()
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

def get_place_id(place_type, location_x, location_y):
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("""SELECT * FROM Places WHERE PlaceType = %s AND
                abs(LocationX - %s) < 0.0000000000001 AND 
                abs(LocationY - %s) < 0.0000000000001 LIMIT 1""",
                (place_type, location_x, location_y))
        conn.commit()
        return c.fetchone()[0]
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def get_place_type(pid):
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("SELECT PlaceType FROM Places WHERE ID = %s LIMIT 1", (pid,))
        result = c.fetchone()
        return result[0] if result else None
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

# TODO merge this with get_place_location_y because stop being stupid
def get_place_location_x(pid):
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("SELECT LocationX FROM Places WHERE ID = %s LIMIT 1", (pid,))
        result = c.fetchone()
        return result[0] if result else None
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def get_place_location_y(pid):
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("SELECT LocationY FROM Places WHERE ID = %s LIMIT 1", (pid,))
        result = c.fetchone()
        return result[0] if result else None
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def get_place_rating(pid):
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("SELECT Rating FROM Reviews WHERE PlacesID = %s", (pid,))
        result = c.fetchall()
        print "get place rating: " + str(result)
        if result:
            ans = 0
            count = 0
            for val in result:
                ans += val[0]
                count += 1
            return float(ans)/count
        return None
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
            "type": place[2],
            "position": [place[3], place[4]],
            "finder": str(place[6]),
        }
        ans.append(place_dict)
    return ans

def get_local_places(location_x, location_y, radius):
    conn = dbhelper.connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("""SELECT * FROM PLACES WHERE abs(LocationX-%s) <= %s AND
        abs(LocationY-%s) <= %s AND (LocationX-%s)^2 +
        (LocationY-%s)^2 <= %s""",
        (location_x, radius, location_y, radius, location_x, location_y,
            radius**2))
        conn.commit()
        return dictionarify(c.fetchall())
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def add_place_report(reporter_id, reported_id, reason):
    global ID_REPORTS_PLACES, PLACE_REPORT_LIMIT
    ruid = dbhelper.generate_id(ID_REPORTS_PLACES)
    if not ruid[0]:
        return (False, "UUID error")
    conn = connect()
    if conn == None:
        return (False, "Database Error")
    c = conn.cursor()
    try:
        c.execute("""INSERT INTO ReportsPlaces (ID, ReportID, ReporterId,
            ReportedId, Reason)  VALUES (%s, %s, %s, %s, %s)""",
                (ruid[1], ruid[1], reporter_id, reported_id, reason))
        conn.commit()
        if get_num_reports_for_place(reported_id) >= PLACE_REPORT_LIMIT:
            remove_place_by_id(reported_id)
            # TODO perhaps, add an intermediary disabled state, rather than
            # automatically removing the place
        return (True, "Place report successful")
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def remove_place_report(reporter_id, reported_id):
    conn = connect()
    if conn == None:
        return (False, "Database Error")
    c = conn.cursor()
    try:
        c.execute("""REMOVE FROM ReportsPlaces WHERE ReporterId = %s AND
            ReportedId = %s """, (reporter_id, reported_id))
        conn.commit()
        return (True, "Place report removal successful")
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def is_place_reported_by(reporter_id, reported_id):
    conn = connect()
    if conn == None:
        return (False, "Database Error")
    c = conn.cursor()
    try:
        c.execute("""SELECT 1 FROM ReportsPlaces WHERE ReporterId = %s AND
            ReportedId = %s LIMIT 1 """, (reporter_id, reported_id))
        return c.fetchone()
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def can_place_be_reported(reporter_id, reported_id):
    return get_place_finder(reported_id) != reporter_id and\
            not is_place_reported_by(reporter_id, reported_id)

def get_num_reports_for_place(reported_id):
    conn = dbhelper.connect()
    if conn == None:
        return (False, "Database Error")
    c = conn.cursor()
    try:
        c.execute("""SELECT 1 FROM ReportsPlaces WHERE ReportedId = %s""",
                (reported_id,))
        return len(c.fetchall())
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

