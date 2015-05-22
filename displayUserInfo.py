import psycopg2

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
        print c.fetchall()
    except:
        print "fail"


if ("places",) in tables_list:
    try:
        #next two lines show previous contents in table Places
        c.execute("SELECT * FROM Places")
        print c.fetchall()
    except:
        print "fail"

if ("reviews",) in tables_list:
    try:
        #next two lines show previous contents in table Places
        c.execute("SELECT * FROM Reviews")
        print c.fetchall()
    except:
        print "fail"

conn.commit()
