from models import Feature, House, Room, Users, db

from app import create_app


def add_user(username, email):
    new_user = Users(username=username, email=email)
    db.session.add(new_user)
    return new_user


def add_house(title, construction_year, owner):
    new_house = House(
        title=title, construction_year=construction_year, owner=owner)
    db.session.add(new_house)
    return new_house


def add_room(name, house):
    new_room = Room(name=name, house=house)
    db.session.add(new_room)
    return new_room


def add_feature(description, room):
    new_feature = Feature(description=description, room=room)
    db.session.add(new_feature)


def populate_db():
    for i in range(1, 5):
        user = add_user(f'user{i}', f'user{i}@example.com')
        house = add_house(f"House of user{i}", 2024, user)
        room = add_room(f"Living room", house)
        add_feature(f"User{i} renovated something", room)


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        populate_db()
