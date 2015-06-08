#Install PostgreSQL database
`sudo apt-get install postgresql postgresql-contrib`  

#Simple PostgreSQL setup
Create a database superuser with the user's username:  
`sudo -u postgres createuser --superuser $USER`  

##Set user password:
`sudo -u postgres psql`  
Type `\password $USER` at the prompt to set the password  

##Initial database setup
The PostgreSQL client by default tries to connect to a database with the same  name as the user's username, so we'll create a new database whose name is our username:  
`sudo -u postgres createdb $USER`  
Now we can connect to the database with: `psql` and create a new database: `create database userdb;`  

#Install required Python packages
`pip install validate_email`  
`pip install psycopg2`  
`pip install Pillow`  
`pip install qrencode`  
`pip install flask_limiter`  

#Install libjpeg-dev for image manipulation
`sudo apt-get install libjpeg-dev`
