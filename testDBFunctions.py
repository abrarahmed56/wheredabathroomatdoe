import dbhelper
import constants
from dbhelper import *

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

if not email_exists("test@chesley.party"):
    print "email1 no exist (should always occur)"
    uuid = generate_id(constants.ID_USER)
    if uuid[0]:
        add_user(uuid[1], "test@chesley.party", "p4s5w0rD", "0123456789", None)
else:
    print("test email1 added again (you screwed something up, unless you dropped users)")

if not email_exists("test2@chesley.party"):
    print "email2 no exist (correct, should be here)"
    uuid = generate_id(constants.ID_USER)
    if not uuid[0]:
        add_user(uuid[1], "test2@chesley.party", "p4s5w0rD", "0123456789", None)
if email_exists("test2@chesley.party"):
    remove_user(get_user_id("test2@chesley.party"))
    print("test email2 deleted (also correct, also should be here)")

print "users:"
for user in get_users_list():
    print user
add_place("bench", 1, 1, "test@chesley.party")
print "added bench at 1, 1\n"
print get_places()
print "added another bench at 1, 1-- should print location already added\n"
print add_place("bench", 1, 1, "test@chesley.party")
print get_places()
remove_place("bench", 1, 1)
print get_places()
print "removed bench at 1,1\n"
print add_place("bench", 1, 1, "test@chesley.party")
print get_places()
print "re-added bench at 1, 1\n"
print get_places()
print "get local places 1 unit away from 3, 3:\n"
print get_local_places(3, 3, 1)
print "get local places 4 units away from 3, 3:\n"
print get_local_places(3, 3, 4)
print get_local_places(1, 1, 0)[0]['ID']
print "adding review:"
add_review(get_local_places(1, 1, 0)[0]['ID'], "test@chesley.party", 10, "10/10 would sit again")
print get_reviews(get_local_places(1, 1, 0)[0]['ID'])
