import os

from flask import Flask
from flask import render_template

from flaskext.markdown import Markdown

import sys
import resource

def create_app(test_config=None):
    """Create and configure the Flask app."""
    app = Flask(__name__, instance_relative_config=True)
    """
    app.config.from_mapping(
        SECRET_KEY=b'`+\xf7\xfdq\x18\x08L<\xfaKfb}\xed\x11',
        # DATABASE=os.path.join(app.instance_path, 'arxiv_interactive.sqlite'),
        # DATABASE=os.path.join("/home/rte/data/db/", "arxiv_db_images_600k.sqlite3"),
        # DATABASE_FTS=os.path.join("/home/rte/data/db/", "arxiv_db_images_600k_single.sqlite3")
        DATABASE=os.path.join("/home/rte/data/db/", "arxiv_db_images_600k_single.sqlite3")
    )
    """

    app.config.from_pyfile("config.py")

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    if app.config["TESTING"]:
        def memory_limit():
            max_mem = 2.5 * 1000000000 # Gigabytes
            soft, hard = resource.getrlimit(resource.RLIMIT_AS)
            print(f'memory limits - soft: {soft} - hard: {hard}')
            resource.setrlimit(resource.RLIMIT_AS, (max_mem, hard))
        memory_limit()

    # register the database commands
    from imagemesh import db
    db.init_app(app)

    # construct a Markdown using flask instance
    Markdown(app)

    # apply the blueprints to the app
    from imagemesh import core
    app.register_blueprint(core.bp)

    return app

# if __name__ = "__main__":
app = create_app()
