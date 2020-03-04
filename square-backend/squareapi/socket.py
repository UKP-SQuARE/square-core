from flask_socketio import SocketIO, emit
from jsonschema import validate, ValidationError
from flasgger.utils import get_schema_specs

socketio = SocketIO(cors_allowed_origins="*")


def init_socket(_skillSelector, _swagger):
    """
    Set the skill selector and swagger used for the sockets
    :param _skillSelector: the skill selector
    :param _swagger: the flasgger swagger object
    """
    global skillSelector
    global swagger
    skillSelector = _skillSelector
    swagger = _swagger


@socketio.on("query", namespace="/api")
def handle_query(json):
    try:
        scheme = get_schema_specs("Query", swagger)["definitions"]["Query"]
        validate(json, scheme)
    except ValidationError as e:
        emit("skillResult", {"error_msg": "Invalid query: {}".format(e)}) # error is already used by skillResult so error_msg it is
    else:
        for result in skillSelector.query(json, generator=True):
            emit("skillResult", result)
        emit("skillResult", {"finished": True})
