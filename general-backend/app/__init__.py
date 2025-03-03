from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()



def create_app():
    app = Flask(__name__)
    CORS(app)


    app.config.from_object("app.config.Config")

    db.init_app(app)
    Migrate(app, db)


    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app
