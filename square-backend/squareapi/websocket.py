from flask_socketio import SocketIO, emit
from flask import current_app as app
from jsonschema import validate, ValidationError
from flasgger.utils import get_schema_specs
import logging

logger = logging.getLogger(__name__)
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
    """
    Handler for query events.
    The skills chosen by the selector are queried and their results are retuned once they are sent back by the skill.

    Emit is done with the 'skillResult' event.
    Either a SkillResult object (see api.py/query(), an error message or an indication that all skills have answered is emitted.
    :param json: Specified by Query scheme. See api.py/query() for more information
    """
    try:
        scheme = get_schema_specs("Query", swagger)["definitions"]["Query"]
        validate(json, scheme)
    except ValidationError as e:
        logger.debug("JSON Validation Error: "+e)
        emit("skillResult", {"error_msg": "Invalid query: {}".format(e)}) # error is already used by skillResult so error_msg it is
    else:
        logger.debug("Query request: {}".format(json))
        logger.info("Query with question: '{}'".format(json["question"]))
        skillResults = skillSelector.query(json, generator=True)
        for result in skillResults:
            emit("skillResult", result)
        emit("skillResult", {"finished": True})


@socketio.on("train", namespace="/api")
def handle_train(json):
    file_size = len(json["file"])
    if file_size > app.config["MAX_CONTENT_LENGTH"]:
        max_len = app.config["MAX_CONTENT_LENGTH"]/(1024*1024)
        emit("train", {"error": "File is too large. Maximum file size is {:.2f}MB".format(max_len)})
    else:
        sentences = json["file"].decode("utf-8").split("\n")
        emit("train", {"finished": True})


@socketio.on("unpublish", namespace="/api")
def handle_unpublish(json):
    emit("unpublish", {"finished": True})