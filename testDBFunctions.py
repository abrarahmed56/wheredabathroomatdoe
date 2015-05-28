import dbhelper
dbhelper.addPlace("bench", 1, 1, "me")
print "added bench at 1, 1\n"
print dbhelper.getPlaces()
print "added another bench at 1, 1-- should print location already added\n"
print dbhelper.addPlace("bench", 1, 1, "me")
print dbhelper.getPlaces()
dbhelper.removePlace("bench", 1, 1)
print "removed bench at 1,1\n"
print dbhelper.addPlace("bench", 1, 1, "me")
print dbhelper.getPlaces()
print "re-added bench at 1, 1\n"
print dbhelper.getPlaces()
print "get local places 1 unit away from 3, 3:\n"
print dbhelper.getLocalPlaces(3, 3, 1)
print "get local places 4 units away from 3, 3:\n"
print dbhelper.getLocalPlaces(3, 3, 4)
