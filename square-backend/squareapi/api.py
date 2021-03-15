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
from squareapi.models import db, User, Skill
from .skill import SkillSelector
from .emailService.utils import send_confirmation_email,send_password_reset_email
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime
import requests

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

skillSelector = SkillSelector()

@api.teardown_request
def session_remove(exception):
    """
    Remove session after request
    Required because we use custom created scopes
    """
    db.session.remove()

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
    try:
        username = request.json["username"]
        password = request.json["password"]
        email = request.json["email"]
        user = User(username, email, password)
        db.session.add(user)
        db.session.commit()

        send_confirmation_email(email)
    except IntegrityError:
        db.session.rollback()
        return jsonify({"msg": "Email already exists."}), 403
    logger.info("Created new user '{}'".format(username))
    return jsonify({"msg": "Thanks for registering. Please check your email to confirm your email address."}), 201


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

@api.route('/confirmEmail', methods=['POST'])
def confirmEmail():
    try:
        token = request.json["token"]
        confirm_serializer = URLSafeTimedSerializer("square2020")

        email = confirm_serializer.loads(token, salt='email-confirmation-salt', max_age=3600)
        user = User.get_user_by_email(email)
    except:
        return jsonify({"message":"The confirmation link is invalid or has expired."}), 403

    if user.email_confirmed:
        return jsonify({"message":"Account already confirmed. Please login!"}), 403
    else:
        user.email_confirmed = True
        user.email_confirmed_on = datetime.now()
        db.session.add(user)
        db.session.commit()
        return jsonify({"message":"Thank you for confirming your email address. Please login !"}), 200


@api.route('/requestresetPassword', methods=['GET', 'POST'])
def requestresetPassword():

    email = request.json["email"]
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"message":"Please check your email. This email is invalid"}),403
    elif user.email_confirmed == True:
        send_password_reset_email(user.email)
        return jsonify({"message":"Please check your email for a password reset link."}),200
    else:
         return jsonify({"message":"Your email address must be confirmed before attempting a password reset."}),403

@api.route('/validatenewPassword', methods=['POST','GET'])
def validatenewPassword():
    try:
        token = request.json["token"]
        new_password = request.json["password"]
        confirm_serializer = URLSafeTimedSerializer("square2020")
    except:
        return jsonify({"message":"The confirmation link is invalid or has expired."}), 401

    email = confirm_serializer.loads(token, salt='password-reset-salt', max_age=3600)
    user = User.get_user_by_email(email)

    user.set_password(new_password)
    db.session.flush()
    db.session.commit()

    return jsonify({"message":"Your password has been updated!"}), 200

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
    logger.info("{} created new skill '{}'".format(user["username"], skill_data["name"]))
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
            logger.info("{} tried to change skill '{}' which does not belong to them".format(user["username"], skill_data["username"]))
        else:
            logger.info("{} tried to change skill with id '{}' which does not exist".format(user["username"], id))
        return jsonify({"msg": "No skill found with id {}".format(id)}), 404
    skill.update(skill_data)
    try:
        db.session.commit()
    except IntegrityError:
        return jsonify({"msg": "Skill name already exists."}), 403
    except Exception as e:
        return jsonify({"msg": "Failed to update the skill. {}".format(e)}), 403
    logger.info("{} updated skill '{}'".format(user["username"], skill_data["name"]))
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
            logger.info("{} tried to delete skill '{}' which does not belong to them".format(user["username"], skill.name))
        else:
            logger.info("{} tried to delete skill with id '{}' which does not exist".format(user["username"], id))
        return jsonify({"msg": "No skill found with id {}".format(id)}), 404
    db.session.delete(skill)
    db.session.commit()
    skillSelector.unpublish(skill.to_dict(), generator=True)
    logger.info("{} deleted skill with id '{}'".format(user["username"], id))
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
          name: train_file
          type: file
          description: the UTF-8 encoded text file containing the training data. Each line represents one sentence.
          required: true
        - in: formData
          name: dev_file
          type: file
          description: the UTF-8 encoded text file containing the dev data. Each line represents one sentence.
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
            logger.info("{} tried to change skill '{}' which does not belong to them".format(user["username"], skill.name))
        else:
            logger.info("{} tried to change skill with id '{}' which does not exist".format(user["username"], id))
        return jsonify({"msg": "No skill found with id {}".format(id)}), 404

    if "train_file" not in request.files or request.files["train_file"].filename == "":
        return jsonify({"msg": "No train file found."}), 404
    train_file = request.files["train_file"]
    train_sentences = []
    for l in train_file.readlines():
        train_sentences.append(l.strip().decode("utf-8"))

    if len(train_sentences) == 0:
        return jsonify({"msg": "Train file is empty."}), 400

    if "dev_file" not in request.files or request.files["dev_file"].filename == "":
        return jsonify({"msg": "No dev file found."}), 404
    dev_file = request.files["dev_file"]
    dev_sentences = []
    for l in dev_file.readlines():
        dev_sentences.append(l.strip().decode("utf-8"))

    if len(dev_sentences) == 0:
        return jsonify({"msg": "Dev file is empty."}), 400

    pool.spawn_n(skillSelector.train, skill.to_dict(), train_sentences, dev_sentences, False)
    logger.info("{} started training for skill '{}'".format(user["username"], skill.name))
    return jsonify({"msg": "Finished training"}), 200

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
            logger.info("{} tried to change skill '{}' which does not belong to them".format(user["username"], skill.name))
        else:
            logger.info("{} tried to change skill with id '{}' which does not exist".format(user["username"], id))
        return jsonify({"msg": "No skill found with id {}".format(id)}), 404

    pool.spawn_n(skillSelector.unpublish, skill.to_dict(), False)
    logger.info("{} started unpublishing for skill '{}'".format(user["username"], skill.name))
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

# @api.route("/getSkills", methods=["GET"])
# def ping():
#     """
#     Endpoint to check if the server is available
#     """
#     endpoint = request.json["skillUrl"]
#     data = requests.get(endpoint+"/ping").json()
#
#     if data["msg"]=="pong" :
#         return jsonify({"msg": "Endpoint exists"}), 200
#     else:
#         return jsonify({"msg": "Endpoint does not exist"}), 404

