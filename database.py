import sqlite3

#Connecting the sqlite database
def create_connection(db_path):
  sqlite_connection = sqlite3.connect(db_path)

return sqlite_connection

  
