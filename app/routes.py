def configure_routes(app):
    @app.route('/')
    def home():
        return "Initial route mainpage"

    @app.route('/house')
    def house():
        return "Initial house page"

    @app.route('/house/rooms')
    def house_rooms():
        return "Initial room page"

    @app.route('/user')
    def user():
        return "Initial user page"
