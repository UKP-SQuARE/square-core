import logging
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    JWTManager, jwt_required, jwt_optional, create_access_token,
    get_jwt_identity
)
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from flasgger import Swagger
import eventlet
from .models import db, User, Skill
from .skill import SkillSelector

api = Blueprint("api", __name__)
jwt = JWTManager()

logger = logging.getLogger(__name__)

# Global Pool
pool = eventlet.GreenPool()

template = {
    "swagger": "2.0",
    "info": {
        "title": "SQuARE Backend",
        "description": "API for the SQuARE backend",
        "contact": {
            "responsibleDeveloper": "Gregor Geigle",
            "email": "gregor.geigle@gmail.com",
        },
        "version": "0.0.1"
    },
    "basePath": "/api",
    "schemes": [
        "http",
        "https"
    ],
}
swagger = Swagger(template=template)


def validation_error_handler(error, _, __):
    """
    Overwrite default flasgger error handler to return the error in a JSON instead of the body
    """
    logger.debug("JSON Validation Error: {}".format(error))
    return jsonify({"msg": "JSON Validation Error: {}".format(error)}), 400


skillSelector = SkillSelector()


@api.route("/register", methods=["POST"])
@swagger.validate("User")
def register():
    """
    Endpoint to create a new user
    ---
    parameters:
        - name: user
          in: body
          type: object
          schema:
            id: User
            $ref: #/definitions/User
          required: true
          description: username and password for the new user
    definitions:
        User:
            type: object
            properties:
                username:
                    type: string
                    description: the username
                    minLength: 1
                password:
                    type: string
                    description: the password
                    minLength: 1
            required: [username, password]
    responses:
        201:
            description: User was created
        403:
            description: Username already exists

    """
    username = request.json["username"]
    password = request.json["password"]
    user = User(username, password)
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        return jsonify({"msg": "Username already exists."}), 403
    logger.info("Created new user '{}'".format(username))
    return jsonify(user.to_dict()), 201


@api.route('/login', methods=['POST'])
@swagger.validate("User", validation_error_handler=validation_error_handler)
def login():
    """
    Endpoint for login with username and password to get a JWT token
    ---
    parameters:
        - name: user
          in: body
          type: object
          schema:
            id: User
            $ref: '#/definitions/User'
          required: true
          description: username and password to login
    definitions:
        Token:
            type: object
            properties:
                token:
                    type: string
                    description: the JWT token for further authentication
    responses:
        200:
            description: User successfully logged in
            schema:
                $ref: '#definitions/Token'

        401:
            description: Wrong username or password
    """
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    user = User.authenticate(username, password)

    if not user:
        logger.debug("Failed login attempt".format(username))
        return jsonify({"msg": "Wrong username or password."}), 401

    access_token = create_access_token(identity=user.to_dict())
    logger.info("{} logged in".format(username))
    return jsonify(token=access_token), 200


@api.route("/skills", methods=["GET"])
@jwt_optional
def get_skills():
    """
    Endpoint to get a list of skill visible to the user. JWT optional.
    Includes skills of the user and published skills.
    ---
    definitions:
        Skill_DB:
            description: Skill model from the DB
            type: object
            properties:
                id:
                    type: integer
                    description: the id of the skill
                name:
                    type: string
                    description: the unique name of the skill
                owner_id:
                    oneOf:
                        - type: string
                        - type: integer
                    description: the id of the owner of this skill
                is_published:
                    type: boolean
                    description: indicates whether a skill is visible to all or only to the owner
                url:
                    type: string
                    description: url to the skill server
                description:
                    type: string
                    description: a short description of the skill
    responses:
        200:
            description: List of skills. Includes skills of user and published skills.
            schema:
                type: array
                items:
                    $ref: '#definitions/Skill_DB'
    """
    user = get_jwt_identity()
    if user:
        skills = Skill.query.filter(or_(Skill.owner_id == user["id"], Skill.is_published.is_(True)))
    else:
        skills = Skill.query.filter(Skill.is_published.is_(True))
    return jsonify([s.to_dict() for s in skills]), 200


@api.route("/selectors", methods=["GET"])
def get_selectors():
    """
    Endpoint to get a list of selector names usable by the server.
    ---
    responses:
        200:
            description: List of selector names.
            schema:
                type: array
                items:
                    type: string
    """
    return jsonify(skillSelector.get_selectors()), 200


@api.route("/skill", methods=["POST"])
@jwt_required
@swagger.validate("Skill", validation_error_handler=validation_error_handler)
def create_skill():
    """
    Endpoint to create a new skill belonging to the user. JWT required.
    ---
    parameters:
        - name: skill
          in: body
          type: object
          schema:
            id: Skill
            $ref: '#/definitions/Skill'
          required: true
          description: the new skill
    definitions:
        Skill:
            type: object
            properties:
                name:
                    type: string
                    description: the unique name of the skill
                    minLength: 1
                url:
                    type: string
                    description: url to the skill server
                    minLength: 1
                description:
                    type: string
                    description: a short description of the skill
            required: [name, url]
    responses:
        200:
            description: Created the skill.
        403:
            description: Skill name already exists
    """
    skill_data = request.json
    user = get_jwt_identity()
    skill = Skill(user=user, skill=skill_data)
    db.session.add(skill)
    try:
        db.session.commit()
    except IntegrityError:
        return jsonify({"msg": "Skill name already exists."}), 403
    except Exception as e:
        return jsonify({"msg": "Failed to create the skill. {}".format(e)}), 403
    logger.info("{} created new skill '{}'".format(user["name"], skill_data["name"]))
    return jsonify(skill.to_dict()), 201


@api.route("/skill/<string:id>", methods=["POST"])
@jwt_required
@swagger.validate("Skill", validation_error_handler=validation_error_handler)
def update_skill(id):
    """
    Endpoint to update a skill belonging to the user. JWT required.
    ---
    parameters:
        - name: id
          in: path
          type: string
          required: true
          description: id of the skill
        - name: skill
          in: body
          type: object
          schema:
            id: Skill
            $ref: '#/definitions/Skill'
          required: true
          description: the new values for the skill. All fields are used so values that should stay the same after the update need to be set as well.
    responses:
        200:
            description: Updated the skill.
        403:
            description: Skill name already exists
        404:
            description: No skill found with the id that belongs to the user
    """
    skill_data = request.json
    user = get_jwt_identity()
    skill = Skill.query.filter_by(id=id).first()
    if not skill or skill.owner_id != user["id"]:
        if skill:
            logger.info("{} tried to change skill '{}' which does not belong to them".format(user["name"], skill_data["name"]))
        else:
            logger.info("{} tried to change skill with id '{}' which does not exist".format(user["name"], id))
        return jsonify({"msg": "No skill found with id {}".format(id)}), 404
    skill.update(skill_data)
    try:
        db.session.commit()
    except IntegrityError:
        return jsonify({"msg": "Skill name already exists."}), 403
    except Exception as e:
        return jsonify({"msg": "Failed to update the skill. {}".format(e)}), 403
    logger.info("{} updated skill '{}'".format(user["name"], skill_data["name"]))
    return jsonify(skill.to_dict()), 200


@api.route("/skill/<string:id>", methods=["DELETE"])
@jwt_required
def delete_skill(id):
    """
    Endpoint to delete a skill belonging to the user. JWT required.
    ---
    parameters:
        - name: id
          in: path
          type: string
          description: id of the skill
    responses:
        200:
            description: Deleted the skill.
        404:
            description: No skill found with the id that belongs to the user
    """
    user = get_jwt_identity()
    skill = Skill.query.filter_by(id=id).first()
    if not skill or skill.owner_id != user["id"]:
        if skill:
            logger.info("{} tried to delete skill '{}' which does not belong to them".format(user["name"], skill.name))
        else:
            logger.info("{} tried to delete skill with id '{}' which does not exist".format(user["name"], id))
        return jsonify({"msg": "No skill found with id {}".format(id)}), 404
    db.session.delete(skill)
    db.session.commit()
    skillSelector.unpublish(skill.to_dict(), generator=True)
    logger.info("{} deleted skill with id '{}'".format(user["name"], id))
    return jsonify(skill.to_dict()), 200


@api.route("/skill/<string:id>/train", methods=["POST"])
@jwt_required
def train_skill(id):
    """
    Endpoint to train a skill belonging to the user with provided training data. JWT required.
    ---
    consumes:
        - multipart/form-data
    parameters:
        - name: id
          in: path
          type: string
          required: true
          description: id of the skill
        - in: formData
          name: file
          type: file
          description: the UTF-8 encoded text file containing the training data. Each line represents one sentence.
          required: true
    responses:
        200:
            description: Started the training.
        404:
            description: No skill found with the id that belongs to the user
    """
    user = get_jwt_identity()
    skill = Skill.query.filter_by(id=id).first()
    if not skill or skill.owner_id != user["id"]:
        if skill:
            logger.info("{} tried to change skill '{}' which does not belong to them".format(user["name"], skill.name))
        else:
            logger.info("{} tried to change skill with id '{}' which does not exist".format(user["name"], id))
        return jsonify({"msg": "No skill found with id {}".format(id)}), 404

    if "file" not in request.files or request.files["file"].filename == "":
        return jsonify({"msg": "No file found."}), 404
    file = request.files["file"]
    sentences = []
    for l in file.readlines():
        sentences.append(l.strip().decode("utf-8"))

    pool.spawn_n(skillSelector.train, skill.to_dict(), sentences, False)
    logger.info("{} started training for skill '{}'".format(user["name"], skill.name))
    return jsonify({"msg": "Started training for the skill"}), 200


@api.route("/skill/<string:id>/unpublish", methods=["POST"])
@jwt_required
def unpublish_skill(id):
    """
    Endpoint to unpublish a skill belonging to the user. JWT required.
    ---
    parameters:
        - name: id
          in: path
          type: string
          required: true
          description: id of the skill
    responses:
        200:
            description: Started the unpublishing.
        404:
            description: No skill found with the id that belongs to the user
    """
    user = get_jwt_identity()
    skill = Skill.query.filter_by(id=id).first()
    if not skill or skill.owner_id != user["id"]:
        if skill:
            logger.info("{} tried to change skill '{}' which does not belong to them".format(user["name"], skill.name))
        else:
            logger.info("{} tried to change skill with id '{}' which does not exist".format(user["name"], id))
        return jsonify({"msg": "No skill found with id {}".format(id)}), 404

    pool.spawn_n(skillSelector.unpublish, skill.to_dict(), False)
    logger.info("{} started unpublishing for skill '{}'".format(user["name"], skill.name))
    return jsonify({"msg": "Started unpublishing for the skill"}), 200





@api.route("/question", methods=["POST"])
@swagger.validate("Query", validation_error_handler=validation_error_handler)
def ask_question():
    """
    Endpoint to ask a question and receive answers from skills.
    ---
    parameters:
        - name: query
          in: body
          type: object
          schema:
            id: Query
            $ref: '#/definitions/Query'
          required: true
          description: the query
    definitions:
        QueryOptions:
            type: object
            properties:
                selector:
                    type: string
                    description: the skill selector the server should use
                    minLength: 1
                selectedSkills:
                    type: array
                    description: the list of skills that the selector can choose from
                    items:
                        $ref: '#definitions/Skill'
                    minItems: 1
                maxQuerriedSkills:
                    type: integer
                    description: the maximum number of skills the selector will query
                    minimum: 1
                maxResultsPerSkill:
                    type: integer
                    description: the maximum number of results from each skill
                    minimum: 1
            required: [selector, selectedSkills, maxQuerriedSkills, maxResultsPerSkill]
        Query:
            type: object
            properties:
                question:
                    type: string
                    description: the question
                    minLength: 1
                options:
                    type: object
                    properties:
                        selector:
                            type: string
                            description: the skill selector the server should use
                            minLength: 1
                        selectedSkills:
                            type: array
                            description: the list of skills that the selector can choose from
                            items:
                                description: Skill model from the DB
                                type: object
                                properties:
                                    id:
                                        type: integer
                                        description: the id of the skill
                                    name:
                                        type: string
                                        description: the unique name of the skill
                                    owner_id:
                                        oneOf:
                                            - type: string
                                            - type: integer
                                        description: the id of the owner of this skill
                                    is_published:
                                        type: boolean
                                        description: indicates whether a skill is visible to all or only to the owner
                                    url:
                                        type: string
                                        description: url to the skill server
                                    description:
                                        type: string
                                        description: a short description of the skill
                                required: [id, name, is_published, url]
                            minItems: 1
                        maxQuerriedSkills:
                            type: integer
                            description: the maximum number of skills the selector will query
                            minimum: 1
                        maxResultsPerSkill:
                            type: integer
                            description: the maximum number of results from each skill
                            minimum: 1
                    required: [selector, selectedSkills, maxQuerriedSkills, maxResultsPerSkill]
                    description: the options for the query
            required: [question, options]
        SkillResult:
            type: object
            properties:
                name:
                    type: string
                    description: the name of the skill
                description:
                    type: string
                    description: a short description of the skill
                score:
                    type: number
                    description: the relevance score for the skill in the range [0;1]
                error:
                    type: string
                    description: error message caused by problems with querying of the skill
                results:
                    type: array
                    items:
                        $ref: '#definitions/ResultEntry'
        ResultEntry:
            type: object
            properties:
                type:
                    type: string
                    enum: [plain_text, raw_html, key_value]
                    description: the format type of the result
                result:
                    description: format depends on type

    responses:
        200:
            description: The results of the query
            schema:
                type: array
                items:
                    $ref: '#/definitions/SkillResult'
    """
    # Bug in flasgger validation with nested $ref so we copy QueryOption and Skill in Query definition
    question_data = request.json
    logger.debug("Query request: {}".format(question_data))
    logger.info("Query with question: '{}'".format(question_data["question"]))
    result = pool.spawn(skillSelector.query, question_data).wait()
    return jsonify(result), 200
