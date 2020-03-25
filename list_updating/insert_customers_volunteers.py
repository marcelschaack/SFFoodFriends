import sqlite3

import csv
from geopy.geocoders import Nominatim

locator = Nominatim(user_agent="SFFoodFriends")

connection = sqlite3.connect('instance/flaskr.sqlite', detect_types=sqlite3.PARSE_DECLTYPES)
db = connection.cursor()
connection.row_factory = sqlite3.Row

with open('list_updating/customers.csv') as csvfile:
    csvdata = csv.reader(csvfile)
    next(csvdata, None)
    for row in csvdata:
        name = row[0]
        type_of_assistance = row[1]
        neighborhood = row[2]
        address = row[3]
        if address is None:
            location = locator.geocode(neighborhood)  # if the address was not inputted, use the neighborhood
        else:
            location = locator.geocode(address)  # if the address is inputted, use the address
        lat_lng = str(location.latitude) + "+" + str(location.longitude)  # location must be tuple for distance function

        email = row[4]
        phone = row[5]
        if row[6] == 'Phone':
            preference = 0
        else:
            preference = 1

        gender = row[7]
        language = row[8]
        if row[9] == 'Yes':
            longterm = 1
        else:
            longterm = 0

        payment = 1
        served = 0

        if db.execute(
                'SELECT id FROM customer WHERE (email = ? AND served = ?)', (email, 0,)
        ).fetchone() is None:
            db.execute(
                'INSERT INTO customer (name, assistancetype, neighborhood, latlng, email, phone, preference, gender, language, longterm, payment, served) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (name, type_of_assistance, neighborhood, lat_lng, email, phone, preference, gender, language, longterm, payment, served)
            )

            connection.commit()

        else:
            print('Customer %s still has an outstanding request!' % email)

with open('list_updating/volunteers.csv', 'r') as csvfile:
    csvdata = csv.reader(csvfile)
    next(csvdata, None)
    for row in csvdata:
        name = row[0]
        area = row[1]
        address = row[2]
        if address is None:
            location = locator.geocode(neighborhood)  # if the address was not inputted, use the neighborhood
        else:
            location = locator.geocode(address)  # if the address is inputted, use the address
        lat_lng = str(location.latitude) + "+" + str(location.longitude)  # location must be tuple for distance function

        email = row[3]
        phone = row[4]
        gender = row[5]
        language = row[6]
        if row[7] == 'Yes':
            longterm = 1
        else:
            longterm = 0
        conditions = 0

        if db.execute(
                'SELECT id FROM volunteer WHERE email = ?', (email,)
        ).fetchone() is None:
            db.execute(
                'INSERT INTO volunteer (name, area, latlng, email, phone, gender, language, longterm, conditions) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (name, area, lat_lng, email, phone, gender, language, longterm, conditions)
            )
            connection.commit()


        else:
            print('Volunteer %s has already signed up!' % email)

connection.close()
