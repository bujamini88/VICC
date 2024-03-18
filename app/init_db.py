import pymysql

# Connection details
db_host = 'db'  # Docker service name
db_user = 'root'
db_password = 'Password'  # Your MariaDB root password
db_name = 'mysql'  # Specify your database name

# Connect to MariaDB database
connection = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)

# Open the schema.sql to read what's inside it
with open('/docker-entrypoint-initdb.d/init.sql') as f:
    with connection.cursor() as cursor:
        cursor.execute(f.read())

# Execute SQL queries to insert data into the database
with connection.cursor() as cursor:
    cursor.execute("INSERT INTO posts (title, content) VALUES (%s, %s)", ('First Post', 'Content for the first post'))
    cursor.execute("INSERT INTO posts (title, content) VALUES (%s, %s)", ('Second Post', 'Content for the second post'))

# Commit the transaction and close the connection
connection.commit()
connection.close()