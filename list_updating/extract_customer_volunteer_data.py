import sqlite3
import csv


connection = sqlite3.connect('instance/flaskr.sqlite', detect_types=sqlite3.PARSE_DECLTYPES)
db = connection.cursor()
connection.row_factory = sqlite3.Row


"""Clear the existing data and create new tables."""
data = db.execute("SELECT * FROM customers")
data2 = db.execute("SELECT * FROM volunteer")
with open('list_updating/results.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerows(data2)
    writer.writerow([' '])
    writer.writerows(data)

with open('flaskr/schema.sql','r') as f:
    db.executescript(f.read().decode('utf8'))
connection.close()
