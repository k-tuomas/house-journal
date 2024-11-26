import os

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate

from .models import Users, db
from .routes import routes_blueprint

DB_URI = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_ADDRESS')}:5432/{os.getenv('POSTGRES_DB')}"
print(f'debug db: {DB_URI}')


def create_app():
    app = Flask(__name__)
    migrate = Migrate(app, db)
    # App configs
    app.config['SECRET_KEY'] = os.getenv(
        'SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'routes.login'

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))

    app.register_blueprint(routes_blueprint)

    return app
