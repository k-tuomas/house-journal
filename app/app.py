import os

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf import CSRFProtect

from .models import Users, db
from .routes import routes_blueprint

load_dotenv()

DB_URI = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@localhost:5432/{os.getenv('POSTGRES_DB')}"


def create_app():
    app = Flask(__name__)
    migrate = Migrate(app, db)
    # App configs
    app.config['SECRET_KEY'] = os.getenv(
        'SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # CSRF protection
    csrf = CSRFProtect(app)

    # Login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'routes.login'

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))

    app.register_blueprint(routes_blueprint)

    return app
