from flask_socketio import SocketIO, emit
from flask import current_app as app
from flask_jwt_extended import decode_token
from jsonschema import validate, ValidationError
from flasgger.utils import get_schema_specs
import logging

from squareapi.models import Skill

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
        logger.debug("JSON Validation Error: {}".format(e))
        emit("skillResult", {"error_msg": "Invalid query: {}".format(e)}) # error is already used by skillResult so error_msg it is
    else:
        logger.debug("Query request: {}".format(json))
        logger.info("Query with question: '{}'".format(json["query"]))
        # Add skill info from DB to query
        skills = Skill.query.filter(Skill.name.in_(json["skills"])).all()
        json["skills"] = [skill.to_dict() for skill in skills]
        skillResults = skillSelector.query(json, generator=True)
        for result in skillResults:
            emit("skillResult", result)
        emit("skillResult", {"finished": True})

# this is ugly but I cannot early return
@socketio.on("train", namespace="/api")
def handle_train(json):
    try:
        train_file = json["train_file"]
        dev_file = json["dev_file"]
        jwt = json["jwt"]
        id = json["id"]
    except KeyError as e:
        emit("train", {"error": "Missing value in request: {}".format(e)})
    else:
        train_file_size = len(train_file)
        dev_file_size = len(dev_file)
        if train_file_size > app.config["MAX_CONTENT_LENGTH"] or dev_file_size > app.config["MAX_CONTENT_LENGTH"]:
            max_len_mb = app.config["MAX_CONTENT_LENGTH"]/(1024*1024)
            emit("train", {"error": "File is too large. Maximum file size is {:.2f}MB".format(max_len_mb)})
        else:
            try:
                jwt = decode_token(jwt)
            except Exception as e:
                emit("train", {"error": "Invalid JWT: {}".format(e)})
            else:
                user = jwt["sub"]
                skill = Skill.query.filter_by(id=id).first()
                if not skill or skill.owner_id != user["id"]:
                    if skill:
                        logger.info("{} tried to train skill '{}' which does not belong to them".format(user["name"], skill.name))
                    else:
                        logger.info("{} tried to train skill with id '{}' which does not exist".format(user["name"], id))
                    emit("train", {"error": "No skill found with id {}".format(id)})
                else:
                    try:
                        train_sentences = train_file.decode("utf-8").split("\n")
                        dev_sentences = dev_file.decode("utf-8").split("\n")
                        if len(train_sentences) == 0:
                            emit("train", {"error": "Train file is empty."})
                        elif len(dev_sentences) == 0:
                            emit("train", {"error": "Dev file is empty."})
                        else:
                            for result in skillSelector.train(skill.to_dict(), train_sentences, dev_sentences, generator=True):
                                emit("train", result)
                            emit("train", {"finished": True})
                    except Exception as e:
                        emit("train", {"error": "Failed to decode file: {}".format(e)})


@socketio.on("unpublish", namespace="/api")
def handle_unpublish(json):
    try:
        jwt = json["jwt"]
        id = json["id"]
    except KeyError as e:
        emit("unpublish", {"error": "Missing value in request: {}".format(e)})
    else:
        try:
            jwt = decode_token(jwt)
        except Exception as e:
            emit("unpublish", {"error": "Invalid JWT: {}".format(e)})
        else:
            user = jwt["sub"]
            skill = Skill.query.filter_by(id=id).first()
            if not skill or skill.owner_id != user["id"]:
                if skill:
                    logger.info("{} tried to unpublish skill '{}' which does not belong to them".format(user["name"], skill.name))
                else:
                    logger.info("{} tried to unpublish skill with id '{}' which does not exist".format(user["name"], id))
                emit("unpublish", {"error": "No skill found with id {}".format(id)})
            else:
                results = skillSelector.unpublish(skill.to_dict(), generator=True)
                for result in results:
                    emit("unpublish", result)
                emit("unpublish", {"finished": True})
