import os

from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, session, url_for)
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from .models import db

routes_blueprint = Blueprint('routes', __name__)


@routes_blueprint.route('/')
def home():
    query = text("SELECT * FROM house WHERE visibility = :visibility")
    result = db.session.execute(query, {'visibility': 'public'})
    public_houses = result.fetchall()
    return render_template('home.html', public_houses=public_houses)


@routes_blueprint.route('/house/<int:id>', methods=['GET', 'POST'])
def house(id):
    # hande comments
    if request.method == 'POST':
        if 'user_id' not in session:
            flash('You need to be logged in to comment.')
            return redirect(url_for('routes.login'))

        content = request.form.get('content')
        if not content:
            flash('Comment content cannot be empty.')
            return redirect(url_for('routes.house', id=id))

        query = text(
            "INSERT INTO comment (content, user_id, house_id) VALUES (:content, :user_id, :house_id)")
        db.session.execute(
            query, {'content': content, 'user_id': session['user_id'], 'house_id': id})
        db.session.commit()

        flash('Comment added successfully.')
        return redirect(url_for('routes.house', id=id))

    # handle house
    house_query = text("SELECT * FROM house WHERE id = :id")
    house_result = db.session.execute(house_query, {'id': id})
    house = house_result.fetchone()

    if not house:
        return "Not found", 404

    rooms_query = text("SELECT * FROM room WHERE house_id = :house_id")
    rooms_result = db.session.execute(rooms_query, {'house_id': id})
    rooms = rooms_result.fetchall()

    house_with_details = {'house': house, 'rooms': []}

    for room in rooms:
        features_query = text("SELECT * FROM feature WHERE room_id = :room_id")
        features_result = db.session.execute(
            features_query, {'room_id': room.id})
        features = features_result.fetchall()

        house_with_details['rooms'].append(
            {'room': room, 'features': features})

    comments_query = text("""
        SELECT comment.id, comment.content, users.username
        FROM comment
        JOIN users ON comment.user_id = users.id
        WHERE comment.house_id = :house_id
    """)
    comments_result = db.session.execute(comments_query, {'house_id': id})
    comments = comments_result.fetchall()

    return render_template('house.html', house=house_with_details, comments=comments)


@routes_blueprint.route('/user/<int:id>')
def user(id):
    query = text("SELECT * FROM users WHERE id = :id")
    result = db.session.execute(query, {'id': id})
    user = result.fetchone()
    if not user:
        return "Not found", 404

    if session.get('user_id') == id:
        house_query = text("SELECT * FROM house WHERE owner_id = :owner_id")
        houses = db.session.execute(house_query, {'owner_id': id}).fetchall()
    else:
        house_query = text(
            "SELECT * FROM house WHERE owner_id = :owner_id AND visibility = :visibility")
        houses = db.session.execute(
            house_query, {'owner_id': id, 'visibility': 'public'}).fetchall()

    houses_with_details = []

    for house in houses:
        room_query = text("SELECT * FROM room WHERE house_id = :house_id")
        rooms = db.session.execute(
            room_query, {'house_id': house.id}).fetchall()

        rooms_with_features = []

        for room in rooms:
            feature_query = text(
                "SELECT * FROM feature WHERE room_id = :room_id")
            features = db.session.execute(
                feature_query, {'room_id': room.id}).fetchall()

            rooms_with_features.append({'room': room, 'features': features})

        houses_with_details.append(
            {'house': house, 'rooms': rooms_with_features})

    return render_template('userpage.html', user=user, houses=houses_with_details)


@routes_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        query = text("SELECT * FROM users WHERE username = :username")
        result = db.session.execute(query, {'username': username})
        user = result.fetchone()

        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
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

        query = text(
            "SELECT * FROM users WHERE username = :username OR email = :email")
        existing_user = db.session.execute(
            query, {'username': username, 'email': email}).first()

        if existing_user:
            flash('Username or email already exists')
            return redirect(url_for('.signup'))

        if not username or len(username) < 3:
            flash('Username must be at least 3 characters long')
            return redirect(url_for('.signup'))
        if not password or len(password) < 6:
            flash('Password must be at least 6 characters long')
            return redirect(url_for('.signup'))

        query = text("""
            INSERT INTO users (username, email, password_hash) 
            VALUES (:username, :email, :password_hash) 
            RETURNING id""")
        result = db.session.execute(query, {
            'username': username,
            'email': email,
            'password_hash': generate_password_hash(password)
        })
        db.session.commit()

        new_user_id = result.fetchone().id
        session['user_id'] = new_user_id
        session['username'] = username
        return redirect(url_for('routes.user', id=new_user_id))
    return render_template('signup.html')


@routes_blueprint.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('routes.home'))


@routes_blueprint.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('You need to be logged in to access the dashboard.')
        return redirect(url_for('routes.login'))
    return "Welcome to your dashboard!"


@routes_blueprint.route('/add_house', methods=['POST'])
def add_house():
    if 'user_id' not in session:
        flash('You need to be logged in to perform this action.')
        return redirect(url_for('routes.login'))

    title = request.form['title']
    construction_year = request.form['construction_year']
    visibility = request.form['visibility']
    image = request.files['image']

    query = text("""
        INSERT INTO house (title, construction_year, owner_id, visibility) 
        VALUES (:title, :construction_year, :owner_id, :visibility) 
        RETURNING id""")
    result = db.session.execute(query, {
        'title': title,
        'construction_year': int(construction_year),
        'owner_id': session['user_id'],
        'visibility': visibility
    })
    db.session.commit()

    new_house_id = result.fetchone().id

    if image and image.filename.endswith('.jpg'):
        filename = secure_filename(f"house_{new_house_id}.jpg")
        filepath = os.path.join(current_app.root_path,
                                'static/images', filename)
        image.save(filepath)

    flash('New house added successfully!')
    return redirect(url_for('routes.home'))


@routes_blueprint.route('/delete_house/<int:id>', methods=['POST'])
def delete_house(id):
    if 'user_id' not in session:
        flash('You need to be logged in to perform this action.')
        return redirect(url_for('routes.login'))

    query = text("SELECT * FROM house WHERE id = :id")
    result = db.session.execute(query, {'id': id})
    house = result.fetchone()
    if not house:
        return "Not found", 404

    if house.owner_id != session['user_id']:
        flash('You do not have permission to delete this house.')
        return redirect(url_for('routes.user', id=session['user_id']))

    image_path = os.path.join(current_app.root_path,
                              'static/images', f"house_{house.id}.jpg")
    if os.path.exists(image_path):
        os.remove(image_path)

    query = text("DELETE FROM house WHERE id = :id")
    db.session.execute(query, {'id': id})
    db.session.commit()

    flash('House deleted')
    return redirect(url_for('routes.user', id=session['user_id']))


@routes_blueprint.route('/add_room/<int:house_id>', methods=['POST'])
def add_room(house_id):
    if 'user_id' not in session:
        flash('You need to be logged in to perform this action.')
        return redirect(url_for('routes.login'))

    query = text("SELECT * FROM house WHERE id = :id")
    result = db.session.execute(query, {'id': house_id})
    house = result.fetchone()
    if not house:
        return "Not found", 404

    if house.owner_id != session['user_id']:
        flash('You do not have permission to add a room to this house.')
        return redirect(url_for('routes.user', id=session['user_id']))

    room_name = request.form.get('room_name')

    query = text("INSERT INTO room (name, house_id) VALUES (:name, :house_id)")
    print(query)
    db.session.execute(query, {'name': room_name, 'house_id': house_id})
    db.session.commit()

    flash('Room added successfully.')
    return redirect(url_for('routes.user', id=session['user_id']))


@routes_blueprint.route('/add_feature/<int:room_id>', methods=['POST'])
def add_feature(room_id):
    if 'user_id' not in session:
        flash('You need to be logged in to perform this action.')
        return redirect(url_for('routes.login'))

    query = text("""
        SELECT room.id AS room_id, house.owner_id AS owner_id
        FROM room
        JOIN house ON room.house_id = house.id
        WHERE room.id = :room_id
    """)
    result = db.session.execute(query, {'room_id': room_id})
    room_info = result.fetchone()

    if not room_info:
        flash("Room not found.")
        return redirect(url_for('routes.home'))

    if room_info.owner_id != session['user_id']:
        flash('You do not have permission to add a feature to this room.')
        return redirect(url_for('routes.user', id=session['user_id']))

    feature_description = request.form.get('feature_description')
    if not feature_description:
        flash('Feature description is required.')
        return redirect(url_for('routes.user', id=session['user_id']))

    query = text(
        "INSERT INTO feature (description, room_id) VALUES (:description, :room_id)")
    db.session.execute(
        query, {'description': feature_description, 'room_id': room_id})
    db.session.commit()
    flash('Feature added successfully.')

    return redirect(url_for('routes.user', id=session['user_id']))


@routes_blueprint.route('/delete_room/<int:room_id>', methods=['POST'])
def delete_room(room_id):
    if 'user_id' not in session:
        flash('You need to be logged in to perform this action.')
        return redirect(url_for('routes.login'))

    query = text("""
        SELECT room.id AS room_id, house.owner_id AS owner_id
        FROM room
        JOIN house ON room.house_id = house.id
        WHERE room.id = :room_id
    """)
    result = db.session.execute(query, {'room_id': room_id})
    room_info = result.fetchone()

    if not room_info:
        flash("Room not found.")
        return redirect(url_for('routes.home'))

    if room_info.owner_id != session['user_id']:
        flash('You do not have permission to delete this room.')
        return redirect(url_for('routes.user', id=session['user_id']))

    # All features need to be deleted so that the room can be deleted
    delete_features_query = text(
        "DELETE FROM feature WHERE room_id = :room_id")
    db.session.execute(delete_features_query, {'room_id': room_id})

    delete_room_query = text("DELETE FROM room WHERE id = :room_id")
    db.session.execute(delete_room_query, {'room_id': room_id})
    db.session.commit()

    flash('Room and its features deleted successfully.')
    return redirect(url_for('routes.user', id=session['user_id']))


@routes_blueprint.route('/delete_feature/<int:feature_id>', methods=['POST'])
def delete_feature(feature_id):
    if 'user_id' not in session:
        flash('You need to be logged in to perform this action.')
        return redirect(url_for('routes.login'))

    query = text("""
        SELECT feature.id AS feature_id, house.owner_id AS owner_id
        FROM feature
        JOIN room ON feature.room_id = room.id
        JOIN house ON room.house_id = house.id
        WHERE feature.id = :feature_id
    """)
    result = db.session.execute(query, {'feature_id': feature_id})
    feature_info = result.fetchone()

    if not feature_info:
        flash("Feature not found.")
        return redirect(url_for('routes.home'))

    if feature_info.owner_id != session['user_id']:
        flash('You do not have permission to delete this feature.')
        return redirect(url_for('routes.user', id=session['user_id']))

    query = text("DELETE FROM feature WHERE id = :feature_id")
    db.session.execute(query, {'feature_id': feature_id})
    db.session.commit()

    flash('Feature deleted successfully.')
    return redirect(url_for('routes.user', id=session['user_id']))


@routes_blueprint.route('/delete_comment/<int:comment_id>/<int:house_id>', methods=['POST'])
def delete_comment(comment_id, house_id):
    if 'user_id' not in session:
        flash('You need to be logged in to delete comments.')
        return redirect(url_for('routes.login'))

    house_query = text("SELECT owner_id FROM house WHERE id = :house_id")
    house_result = db.session.execute(house_query, {'house_id': house_id})
    house = house_result.fetchone()

    if not house or house.owner_id != session['user_id']:
        flash('You do not have permission to delete this comment.')
        return redirect(url_for('routes.house', id=house_id))

    delete_comment_query = text("DELETE FROM comment WHERE id = :comment_id")
    db.session.execute(delete_comment_query, {'comment_id': comment_id})
    db.session.commit()

    flash('Comment deleted successfully.')
    return redirect(url_for('routes.house', id=house_id))
