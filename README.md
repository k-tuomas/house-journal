# House-journal
This repository is for Helisinki University course "Tietokannat ja web-ohjelmointi" project.

## Overview
House Journal is an app designed for management of home-related information. It allows users to log events, track renovations, store technical data, and set reminders for upcoming maintenance tasks.

## Features

- **User Authentication**: Sign in, sign out, and account creation capabilities.
- **Home Overview**: View a list of properties along with key details such as construction year and owner.
- **Add New House**: Capability to add new properties to your management list.
- **Room and Feature Customization**: Add outhouses, rooms etc. to your property and assign specific features or tasks to each.
- **Comment section**: Add comments to your property or other public properties.
- **Editable Content**: Modify or delete house details and comment threads.
- **Search Functionality**: Ability to search for houses based on specific features.
- **Privacy Settings**: Set your house visibility to private or public. Only public houses can be viewed by others.
- **Admin Controls**: Administrators can add or remove houses from the platform.


## Gettingh started`
Requirements:
- Python12
- Docker

To run the app you need to add .env file to repository root with following values:
```
POSTGRES_DB=<db-name>
POSTGRES_USER=<db-user>
POSTGRES_PASSWORD=<db-password>
SECRET_KEY=<session-secret>
```
The app uses PostgreSQL, it can be run using the docker-compose.yml (e.g run ```docker-compose up``)

To run Flask app, run:
```
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

Note that The actuall login/signup functionality is still work in progress and might not work.