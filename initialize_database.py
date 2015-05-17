import psycopg2

conn = psycopg2.connect("dbname='users' user='softdev'")
c = conn.cursor()

#to delete database:
#sudo -u postgres psql -c "DROP DATABASE users"

#show table names
c.execute("SELECT relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';")
tables_list =  c.fetchall()
print tables_list

if ("users",) in tables_list:
    try:
        #next two lines show previous contents in table Users
        c.execute("SELECT * FROM Users")
        print c.fetchall()
        #delete everything in Users table
        c.execute("DROP TABLE Users")
    except:
        print "fail"
if ("places",) in tables_list:
    try:
        #next two lines show previous contents in table Places
        c.execute("SELECT * FROM Places")
        print c.fetchall()
        #delete everything in Places table
        c.execute("DROP TABLE Places")
    except:
        print "fail"

#create new Users and Places table
c.execute("CREATE TABLE Users (Email TEXT, Password TEXT)")
c.execute("CREATE TABLE Places (Name TEXT, Location TEXT, Favorites INT)")
conn.commit()
