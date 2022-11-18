# imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import secrets
from os import path

# define constant
DB_NAME = "database.db"

# create the extension
db = SQLAlchemy()

def create_app():

    # create the app
    app = Flask(__name__)

    # configure the SQLite database, relative to the app instance folder
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"

    # initialize the app with the extension
    db.init_app(app)

    # creo chiave segreta
    #secret = secrets.token_urlsafe(32)
    #app.secret_key = secret

    # register the blueprint
    from .views import views
    app.register_blueprint(views, url_prefix='/')

    isDatabaseExist = path.exists('instance/' + DB_NAME)

    with app.app_context():
        db.create_all()
        db.session.commit()
        print('Created Database')

    # Seed database
    if not isDatabaseExist:
        from website.views import riempi
        with app.app_context():
            riempi()
    
    return app