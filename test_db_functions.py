from constants import *
from dbhelper import *
import uuid

def get_users_list():
    conn = connect()
    if conn == None:
        return "Database Error"
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM USERS")
        conn.commit()
        return c.fetchall()
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
    finally:
        if conn:
            conn.close()

def display_places(places, s):
    print "Displaying " + s + ":"
    for place in places:
        print place

if not email_exists("test@www.chesley.party"):
    print "email1 no exist (should always occur)"
    _uuid = generate_id(ID_USER)
    if _uuid[0]:
        add_user(_uuid[1], "test@www.chesley.party", "p4s5w0rD", "0123456789", None)
else:
    print("test email1 added again (you screwed something up, unless you dropped users)")

if not email_exists("test2@www.chesley.party"):
    print "email2 no exist (correct, should be here)"
    _uuid = generate_id(ID_USER)
    if not _uuid[0]:
        add_user(_uuid[1], "test2@www.chesley.party", "p4s5w0rD", "0123456789", None)
if email_exists("test2@www.chesley.party"):
    remove_user(get_user_id("test2@www.chesley.party"))
    print("test email2 deleted (also correct, also should be here)")

print "users:"
for user in get_users_list():
    print user

add_place("bench", 1, 1, "test@www.chesley.party")
print "added bench at 1, 1\n"
print "added another bench at 1, 1-- should print location already added in next line"
print add_place("bench", 1, 1, "test@www.chesley.party")
display_places(get_places(), "all places")
print "\n"
print "remove bench at 1,1:"
print remove_place("bench", 1, 1)
display_places(get_places(), "all places")
print "\n"
print "re-add bench at 1, 1:"
print add_place("bench", 1, 1, "test@www.chesley.party")
display_places(get_places(), "all places")
print "\n"
display_places(get_local_places(3, 3, 1), "local places 1 unit from (3, 3)--should display no results")
print "\n"
display_places(get_local_places(3, 3, 4), "local places 4 units from (3, 3)--should display added bench, and nothing else, assuming nobody uses the app who lives at (1, 1)")
print "\n"
display_places(get_local_places(1, 1, 0), "local places 0 units from (1, 1)")
print "ID of bench that was added: " + get_local_places(1, 1, 0)[0]['ID']
print "ID of bench that was added again: " + str(get_place_id("bench", 1, 1))
print "adding review:"
add_review(get_local_places(1, 1, 0)[0]['ID'], "test@www.chesley.party", 10, "10/10 would sit again")
print get_reviews(get_local_places(1, 1, 0)[0]['ID'])
tmp_url_uuid = add_temporary_url(get_user_id("test@www.chesley.party"),
        TEMP_URL_EMAIL_CONFIRM)[1]
print "Temporary url uuid: " + str(tmp_url_uuid)
print get_temporary_url(tmp_url_uuid,
        get_user_id("test@www.chesley.party"), TEMP_URL_EMAIL_CONFIRM)
