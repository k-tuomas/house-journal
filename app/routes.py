from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from app.models import House, Users

# Define a blueprint
routes_blueprint = Blueprint('routes', __name__)


@routes_blueprint.route('/')
def home():
    public_houses = House.query.filter_by(visibility='public').all()
    return render_template('home.html', public_houses=public_houses)


@routes_blueprint.route('/house')
def house():
    return "Initial house page"


@routes_blueprint.route('/house/rooms')
def house_rooms():
    return "Initial room page"


@routes_blueprint.route('/user/<int:id>')
def user(id):
    user = Users.query.get(id)
    if user:
        return render_template('userpage.html', user=user)
    else:
        return "User not found", 404


@routes_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = Users.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('routes.user', id=user.id))
        else:
            flash('Invalid username or password')
    return render_template('login.html')


@routes_blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if username or email already exists
        if Users.query.filter_by(username=username).first() or Users.query.filter_by(email=email).first():
            flash('Username or email already exists')
            return redirect(url_for('.signup'))

        new_user = Users(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        from .app import db  # Import db here to avoid circular import
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('routes.user', id=new_user.id))
    return render_template('signup.html')


@routes_blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('routes.home'))


@routes_blueprint.route('/dashboard')
@login_required
def dashboard():
    return "Welcome to your dashboard!"
