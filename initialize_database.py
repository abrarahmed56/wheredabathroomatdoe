import psycopg2
from constants import *

conn = psycopg2.connect("dbname='%s' user='%s'" % (DB_NAME, DB_USER))
c = conn.cursor()

# To create the database:
#sudo -u postgres psql -c "CREATE DATABASE users"
# To delete the database:
#sudo -u postgres psql -c "DROP DATABASE users"
# To list databases:
# >> psql
# <db>=# \l
# To connect to a database:
# >> psql
# <db>=# \connect <dbname>
# To list tables:
# >> psql
# <dbname>=# \dt

USER_TABLE_CREATE = """CREATE TABLE Users (ID UUID PRIMARY KEY, UserID UUID, Email TEXT,
    Password TEXT, Phone TEXT, FirstName varchar(50), LastName
    varchar(50), Bio varchar(250), Disabled BOOLEAN, EmailConfirmed
    BOOLEAN, PhoneConfirmed BOOLEAN)"""

PLACES_TABLE_CREATE = """CREATE TABLE Places (ID UUID PRIMARY KEY, PlaceID UUID,
    PlaceType TEXT, LocationX DOUBLE PRECISION, LocationY DOUBLE PRECISION,
    Favorites INT, Finder UUID REFERENCES Users(ID))"""

# TODO user deletion should not cascade places

REVIEWS_TABLE_CREATE = """CREATE TABLE Reviews (ID UUID PRIMARY KEY, ReviewID
    UUID, PlacesID UUID REFERENCES Places (ID) ON DELETE CASCADE, Username TEXT, Rating INT, Review TEXT)"""

FAVORITES_TABLE_CREATE = """CREATE TABLE Favorites (UserID UUID REFERENCES Users
    (ID) ON DELETE CASCADE, PlacesID UUID REFERENCES Places (ID) ON DELETE
    CASCADE)"""

TEMPORARY_URLS_TABLE_CREATE = """CREATE TABLE TemporaryUrls (ID UUID PRIMARY
KEY, UrlID UUID, CreationTime TIMESTAMP NOT NULL DEFAULT NOW(), ExpiryTime
INTERVAL NOT NULL DEFAULT INTERVAL '1 day', UrlType TEXT,
UserID UUID REFERENCES Users (ID) ON DELETE CASCADE)"""

def drop(dbname):
    c.execute("DROP TABLE %s CASCADE" % dbname)

def migrate(dbname, create_query):
    try:
        # Print contents of table
        c.execute("SELECT * FROM %s" % (dbname,))
        print c.fetchall()
        # Migrate data to new table
        old_col_names = [desc[0] for desc in c.description]
        c.execute("ALTER TABLE %s RENAME TO temp_%s" % (dbname, dbname))
        c.execute(create_query)
        c.execute("SELECT * FROM %s LIMIT 0" % (dbname,))
        new_col_names = [desc[0] for desc in c.description]
        preserved_col_names = [col_name for col_name in new_col_names if
                col_name in old_col_names]
        preserved_col_names = ', '.join(preserved_col_names)
        c.execute("""INSERT INTO %s (%s) SELECT %s from temp_%s""" %
                (dbname, preserved_col_names, preserved_col_names, dbname))
        c.execute("DROP TABLE temp_%s CASCADE" % (dbname,))
    except Exception, e:
        print "Error displaying contents of %s database: %s" % (dbname, e)

# Print existing table names
c.execute("SELECT relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';")
tables_list =  c.fetchall()
print "Table names: "
print tables_list

if ("users",) in tables_list:
    migrate('Users', USER_TABLE_CREATE)
else:
    c.execute(USER_TABLE_CREATE)

if ("places",) in tables_list:
    migrate('Places', PLACES_TABLE_CREATE)
else:
    c.execute(PLACES_TABLE_CREATE)

if ("reviews",) in tables_list:
    migrate('Reviews', REVIEWS_TABLE_CREATE)
else:
    c.execute(REVIEWS_TABLE_CREATE)

if ("favorites",) in tables_list:
    migrate('Favorites', FAVORITES_TABLE_CREATE)
else:
    c.execute(FAVORITES_TABLE_CREATE)

if ("temporaryurls",) in tables_list:
    migrate('TemporaryUrls', TEMPORARY_URLS_TABLE_CREATE)
else:
    c.execute(TEMPORARY_URLS_TABLE_CREATE)

conn.commit()

