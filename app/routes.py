import os

from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from app.models import House, Users

# Define a blueprint
routes_blueprint = Blueprint('routes', __name__)


@routes_blueprint.route('/')
def home():
    public_houses = House.query.filter_by(visibility='public').all()
    return render_template('home.html', public_houses=public_houses)


@routes_blueprint.route('/house/<int:id>')
def house(id):
    house = House.query.get(id)
    if House:
        return render_template('house.html', house=house)
    else:
        return "House not found", 404


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

        if not username or len(username) < 3:
            flash('Username must be at least 3 characters long')
            return redirect(url_for('.signup'))
        if not password or len(password) < 6:
            flash('Password must be at least 6 characters long')
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


@routes_blueprint.route('/add_house', methods=['POST'])
@login_required
def add_house():
    title = request.form['title']
    construction_year = request.form['construction_year']
    visibility = request.form['visibility']
    image = request.files['image']

    new_house = House(
        title=title,
        construction_year=int(construction_year),
        owner_id=current_user.id,
        visibility=visibility
    )
    from .app import db  # Import db here to avoid circular import
    db.session.add(new_house)
    db.session.commit()

    if image and image.filename.endswith('.jpg'):
        filename = secure_filename(f"house_{new_house.id}.jpg")
        filepath = os.path.join(current_app.root_path,
                                'static/images', filename)
        image.save(filepath)

    flash('New house added successfully!')
    return redirect(url_for('routes.home'))
