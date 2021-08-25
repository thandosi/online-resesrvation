import sqlite3


con = sqlite3.connect("reservation.db")
cursor = con.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())
#cursor.execute("DROP TABLE client")
#print("Table dropped")
