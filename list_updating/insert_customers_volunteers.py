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
        if row[4] == 'Phone':
            preference = 0
        else:
            preference = 1
        type_of_assistance = row[3]
        payment = 1
        served = 0

        if db.execute(
            'SELECT id FROM customer WHERE (email = ? AND served = ?)', (email,0,)
        ).fetchone() is None:
            db.execute(
                'INSERT INTO customer (neighborhood, email, phone, preference, assistancetype, payment, served) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (neighborhood, email, phone, preference, type_of_assistance, payment, served)
            )

            connection.commit()

        else:
            print('Customer %s still has an outstanding request!' % email)




with open('list_updating/volunteers.csv', 'r') as csvfile:
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


        else:
            print('Volunteer %s has already signed up!' % email)
connection.close()
