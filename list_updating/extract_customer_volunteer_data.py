import sqlite3
import csv


connection = sqlite3.connect('instance/flaskr.sqlite', detect_types=sqlite3.PARSE_DECLTYPES)
db = connection.cursor()
connection.row_factory = sqlite3.Row


"""Clear the existing data and create new tables."""
data = db.execute("SELECT * FROM customer").fetchall()
data2 = db.execute("SELECT * FROM volunteer").fetchall()
with open('list_updating/results.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerows(data)
    writer.writerow([' '])
    writer.writerows(data2)

with open('flaskr/schema.sql') as f:
    db.executescript(f.read().decode('utf8'))
connection.close()
