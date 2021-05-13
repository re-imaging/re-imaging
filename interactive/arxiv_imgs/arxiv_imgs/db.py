import sqlite3

# import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def get_db2():
    if 'db2' not in g:
        g.db2 = sqlite3.connect(
            current_app.config['DATABASE_FTS'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db2.row_factory = sqlite3.Row

    return g.db2


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)
    # app.cli.add_command(init_db_command)
