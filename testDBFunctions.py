import dbhelper
dbhelper.add_place("bench", 1, 1, "me")
print "added bench at 1, 1\n"
print dbhelper.get_places()
print "added another bench at 1, 1-- should print location already added\n"
print dbhelper.add_place("bench", 1, 1, "me")
print dbhelper.get_places()
dbhelper.remove_place("bench", 1, 1)
print "removed bench at 1,1\n"
print dbhelper.add_place("bench", 1, 1, "me")
print dbhelper.get_places()
print "re-added bench at 1, 1\n"
print dbhelper.get_places()
print "get local places 1 unit away from 3, 3:\n"
print dbhelper.get_local_places(3, 3, 1)
print "get local places 4 units away from 3, 3:\n"
print dbhelper.get_local_places(3, 3, 4)
