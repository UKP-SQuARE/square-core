from squareapi.app import create_app

if __name__ == "__main__":
    socketio, app = create_app()
    socketio.run(app)