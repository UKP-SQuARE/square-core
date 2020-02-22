from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    JWTManager, jwt_required, jwt_optional, create_access_token,
    get_jwt_identity
)
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from flasgger import Swagger
from .models import db, User, Skill
from .skill import SkillSelector

api = Blueprint("api", __name__)
jwt = JWTManager()

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

    return jsonify(user.to_dict()), 201


@api.route('/login', methods=['POST'])
@swagger.validate("User")
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
        return jsonify({"msg": "Wrong username or password."}), 401

    access_token = create_access_token(identity=user.to_dict())
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
                    type: string
                    description: the id of the skill
                name:
                    type: string
                    description: the unique name of the skill
                owner_id:
                    type: string
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
@swagger.validate("Skill")
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
                is_published:
                    type: boolean
                    description: indicates whether a skill is visible to all or only to the owner
                url:
                    type: string
                    description: url to the skill server
                    minLength: 1
                description:
                    type: string
                    description: a short description of the skill
            required: [name, is_published, url]
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
    return jsonify(skill.to_dict()), 201


@api.route("/skill/<string:id>", methods=["POST"])
@jwt_required
@swagger.validate("Skill")
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
        return jsonify({"msg": "No skill found with id {}".format(id)}), 404
    skill.update(skill_data)
    try:
        db.session.commit()
    except IntegrityError:
        return jsonify({"msg": "Skill name already exists."}), 403
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
        return jsonify({"msg": "No skill found with id {}".format(id)}), 404
    db.session.delete(skill)
    db.session.commit()
    return jsonify(skill.to_dict()), 200


@api.route("/question", methods=["POST"])
@swagger.validate("Query")
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
    #Bug in flasgger validation with nested $ref so we copy QueryOption and Skill in Query definition
    question_data = request.json
    return jsonify(skillSelector.query(question_data)), 200
