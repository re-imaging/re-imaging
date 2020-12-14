import os

from flask import Flask
from flask import render_template

def create_app(test_config=None):
    """Create and configure the Flask app."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        # DATABASE=os.path.join(app.instance_path, 'arxiv_interactive.sqlite'),
        DATABASE=os.path.join("/home/rte/data/db/", "arxiv_db_images_600k.sqlite3")
    )

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

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # @app.route('/test')
    # def get_test_image():
    #     """Just show one image as a test
    #     """
    #
    #     # filename = "/home/rte/data/images/web/120k/5478268.jpg"
    #     # filename = os.path.join("static/all", "5478268.jpg")
    #     filename = os.path.join("static/all", "7732085.jpg")
    #     # return f'<img src={filename}>'
    #     return render_template("opening.html", image = filename)

    # register the database commands
    from arxiv_imgs import db

    db.init_app(app)

    # apply the blueprints to the app
    from arxiv_imgs import core

    app.register_blueprint(core.bp)
    # app.register_blueprint(blog.bp)

    # make url_for('index') == url_for('blog.index')
    # in another app, you might define a separate main index here with
    # app.route, while giving the blog blueprint a url_prefix, but for
    # the tutorial the blog will be the main index
    # app.add_url_rule("/", endpoint="index")

    return app
