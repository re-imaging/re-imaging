import sqlite3

from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    if 'db' not in g:
        print(current_app.config['DATABASE'])
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            uri=True,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)
