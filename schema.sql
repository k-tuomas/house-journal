CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255)
);

CREATE TABLE house (
    id SERIAL PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    construction_year INTEGER NOT NULL,
    owner_id INTEGER NOT NULL,
    visibility VARCHAR(50) DEFAULT 'public',
    FOREIGN KEY (owner_id) REFERENCES users(id)
);

CREATE TABLE room (
    id SERIAL PRIMARY KEY,
    house_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    FOREIGN KEY (house_id) REFERENCES house(id)
);

CREATE TABLE feature (
    id SERIAL PRIMARY KEY,
    room_id INTEGER NOT NULL,
    description VARCHAR(255) NOT NULL,
    FOREIGN KEY (room_id) REFERENCES room(id)
);

CREATE TABLE comment (
    id SERIAL PRIMARY KEY,
    content VARCHAR(255) NOT NULL,
    user_id INTEGER NOT NULL,
    house_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (house_id) REFERENCES house(id)
);
