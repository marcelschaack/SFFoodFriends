import sqlite3

import csv


connection = sqlite3.connect('instance/flaskr.sqlite', detect_types=sqlite3.PARSE_DECLTYPES)
db = connection.cursor()
connection.row_factory = sqlite3.Row

with open('list_updating/customers.csv') as csvfile:
    csvdata = csv.reader(csvfile)
    next(csvdata, None)
    for row in csvdata:
        neighborhood = row[0]
        email = row[1]
        phone = row[2]
        type_of_assistance = row[3]
        if row[4] == 'Phone':
            preference = 0
        else:
            preference = 1
        payment = 1
        served = 0

        if db.execute(
            'SELECT id FROM customers WHERE email = ?', (email,)
        ).fetchone() is None:
            db.execute(
                'INSERT INTO customers (neighborhood, email, phone, type_of_assistance, preference, payment, served) '
                'VALUES (?, ?, ?, ?, ?, ?, ?)',
                (neighborhood, email, phone, type_of_assistance, preference, payment, served)
            )
            connection.commit()


with open('list_updating/volunteers.csv') as csvfile:
    csvdata = csv.reader(csvfile)
    next(csvdata, None)
    for row in csvdata:
        email = row[0]
        areas = row[1]

        if db.execute(
            'SELECT id FROM volunteer WHERE email = ?', (email,)
        ).fetchone() is None:
            db.execute(
                'INSERT INTO volunteer (email, areas) VALUES (?, ?)',
                (email, areas)
            )
            connection.commit()
