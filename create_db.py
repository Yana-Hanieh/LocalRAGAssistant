import sqlite3

conn = sqlite3.connect("knowledge.db") #connection between the python programe (sqlite3) and the knowledge.db database file
cursor = conn.cursor() #cursor that executes the commands, it will be used to go through the results row-by-row when the queries are ran

#create the main storage table for document chunks and vector embeddings
cursor.execute("""
    CREATE TABLE IF NOT EXISTS chunks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT NOT NULL,
        content TEXT NOT NULL,
        embedding TEXT NOT NULL
    );
""")

conn.commit() #saves the changes made
conn.close() #close the connection (release the db file/connection)

print("Database and table created successfully.")