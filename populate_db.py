from app import create_app
from app.models import Feature, House, Room, Users, db


def add_user(username, email):
    existing_user = Users.query.filter_by(username=username).first()
    if not existing_user:
        new_user = Users(username=username, email=email)
        db.session.add(new_user)
        return new_user
    return existing_user


def add_house(title, construction_year, owner):
    existing_house = House.query.filter_by(title=title, owner=owner).first()
    if not existing_house:
        new_house = House(
            title=title, construction_year=construction_year, owner=owner)
        db.session.add(new_house)
        return new_house
    return existing_house


def add_room(name, house):
    existing_room = Room.query.filter_by(name=name, house=house).first()
    if not existing_room:
        new_room = Room(name=name, house=house)
        db.session.add(new_room)
        return new_room
    return existing_room


def add_feature(description, room):
    existing_feature = Feature.query.filter_by(
        description=description, room=room).first()
    if not existing_feature:
        new_feature = Feature(description=description, room=room)
        db.session.add(new_feature)
        return new_feature
    return existing_feature


def populate_db():
    for i in range(1, 5):
        print(f'Adding user {i} to database')
        user = add_user(f'user{i}', f'user{i}@example.com')
        house = add_house(f"House of user{i}", 2024, user)
        room = add_room(f"Living room", house)
        add_feature(f"User{i} renovated something", room)

    db.session.commit()


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        populate_db()
