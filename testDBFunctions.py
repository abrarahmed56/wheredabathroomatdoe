import dbhelper
import constants
if not dbhelper.email_exists("test@chesley.party"):
    print "email no exist"
    uuid = dbhelper.generate_id(constants.ID_USER)
    if not uuid[0]:
        add_user(uuid[1], "test@chesley.party", "p4s5w0rD", "0123456789", None)
else:
    #remove_user("test@www.chesley.party")
    print("test email already added")
print "users:"
for user in dbhelper.get_users_list():
    print user
dbhelper.add_place("bench", 1, 1, "a@a.com")
print "added bench at 1, 1\n"
print dbhelper.get_places()
print "added another bench at 1, 1-- should print location already added\n"
print dbhelper.add_place("bench", 1, 1, "test@chesley.party")
print dbhelper.get_places()
dbhelper.remove_place("bench", 1, 1)
print dbhelper.get_places()
print "removed bench at 1,1\n"
print dbhelper.add_place("bench", 1, 1, "test@chesley.party")
print dbhelper.get_places()
print "re-added bench at 1, 1\n"
print dbhelper.get_places()
print "get local places 1 unit away from 3, 3:\n"
print dbhelper.get_local_places(3, 3, 1)
print "get local places 4 units away from 3, 3:\n"
print dbhelper.get_local_places(3, 3, 4)
print dbhelper.get_local_places(1, 1, 0)[0]['ID']
print "adding review:"
dbhelper.add_review(dbhelper.get_local_places(1, 1, 0)[0]['ID'], "test@chesley.party", 10, "10/10 would sit again")
print dbhelper.get_reviews(dbhelper.get_local_places(1, 1, 0)[0]['ID'])
