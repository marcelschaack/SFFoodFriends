import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext
import csv


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(drop_db_command)


@click.command('drop-db')
@with_appcontext
def drop_db_command():
    """Clear the existing data and create new tables."""
    connection = sqlite3.connect(current_app.config['DATABASE'], detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = connection.cursor()
    data = cursor.execute("SELECT * FROM customers")
    # data2 = cursor.execute("SELECT * FROM volunteer")
    with open('results.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(data)
        # writer.writerows(data2)

    #    cursor.execute("DROP TABLE customers")
    #    cursor.execute("DROP TABLE volunteer")
    close_db()
#    click.echo('Dropped the database')
