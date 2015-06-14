import psycopg2
import dbhelper

conn = psycopg2.connect("dbname='users' user='softdev'")
c = conn.cursor()

#show table names
c.execute("SELECT relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';")
tables_list =  c.fetchall()
print tables_list

if ("users",) in tables_list:
    try:
        #next two lines show previous contents in table Users
        c.execute("SELECT * FROM Users")
        print "User info:"
        print c.fetchall()
    except:
        print "fail"


if ("places",) in tables_list:
    try:
        #next two lines show previous contents in table Places
        c.execute("SELECT * FROM Places")
        print "Places info:"
        for x in c.fetchall():
            print x
    except:
        print "fail"

if ("reviews",) in tables_list:
    try:
        #next two lines show previous contents in table Places
        c.execute("SELECT * FROM Reviews")
        print "Reviews info:"
        #print c.fetchall()
    except:
        print "fail"

if ("favorites",) in tables_list:
    try:
        #next two lines show previous contents in table Places
        c.execute("SELECT * FROM Favorites")
        print "Favorites info:"
        results = c.fetchall()
        for x in results:
            user = dbhelper.get_user_email(x[0])
            place = dbhelper.get_place_type(x[1])
            placeX = dbhelper.get_place_location_x(x[1])
            placeY = dbhelper.get_place_location_y(x[1])
            print "user: " + user + "\nplace: " + place + "\nplaceX: " + str(placeX) + "\nplaceY: " + str(placeY) + "\n"
        print results
    except:
        print "fail"

conn.commit()
