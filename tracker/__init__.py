import os

from flask import Flask
from flask_jwt_extended import JWTManager
from flask import current_app, g


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SERVER_NAME='localhost:5000',
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'tracker.sqlite'),
        JWT_SECRET_KEY='super-secret',
        JWT_TOKEN_LOCATION='headers',
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Register the database
    from .model import db
    db.init_app(app)

    JWTManager(app)

    # Register blueprints
    from . import auth, dashboard, index, api
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(index.bp)
    app.register_blueprint(api.bp)

    app.before_request(auth.load_logged_in_user)

    #app.add_url_rule('/', endpoint='index')
    return app
