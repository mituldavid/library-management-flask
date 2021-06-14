import mysql.connector


# Function to run .sql file
def executeScriptsFromFile(filename):
    # Open and read the file as a single buffer
    fd = open(filename, 'r')
    sqlFile = fd.read()
    fd.close()

    # All SQL commands (split on ';')
    sqlCommands = sqlFile.split(';')
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",  # change as required
        passwd="root",  # change as required
    )
    c = mydb.cursor()

    # Execute every command from the input file
    for command in sqlCommands:
        # This will skip and report errors
        try:
            c.execute(command)
        except (mysql.connector.Error) as e:
            print(e)
    mydb.commit()
    mydb.close()


# Setup main database
executeScriptsFromFile('LibraryDB.sql')
# Setup database for unit testing
executeScriptsFromFile('LibraryTestDB.sql')
