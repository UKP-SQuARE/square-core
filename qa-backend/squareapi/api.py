from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    JWTManager, jwt_required, jwt_optional, create_access_token,
    get_jwt_identity
)
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from .models import db, User, Skill
from .skill import SkillSelector

api = Blueprint("api", __name__)
jwt = JWTManager()
skillSelector = SkillSelector()


@api.route("/register", methods=["POST"])
def register():
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
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    user = User.authenticate(username, password)

    if not user:
        return jsonify({"msg": "Wrong username or password."}), 401

    access_token = create_access_token(identity=user.identity())
    return jsonify(token=access_token), 200


@api.route("/skills", methods=["GET"])
@jwt_optional
def get_skills():
    user = get_jwt_identity()
    if user:
        skills = Skill.query.filter(or_(Skill.owner_id == user["id"], Skill.is_published.is_(True)))
    else:
        skills = Skill.query.filter(Skill.is_published.is_(True))
    return jsonify([s.to_dict() for s in skills]), 200


@api.route("/selectors", methods=["GET"])
def get_selectors():
    return jsonify(skillSelector.get_selectors()), 200


@api.route("/skill", methods=["POST"])
@jwt_required
def create_skill():
    skill_data = request.json["skill"]
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
def update_skill(id):
    skill_data = request.json["skill"]
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
    user = get_jwt_identity()
    skill = Skill.query.filter_by(id=id).first()
    if not skill or skill.owner_id != user["id"]:
        return jsonify({"msg": "No skill found with id {}".format(id)}), 404
    db.session.delete(skill)
    db.session.commit()
    return jsonify(skill.to_dict()), 200


@api.route("/question", methods=["POST"])
def ask_question():
    question_data = request.json
    return jsonify(skillSelector.query(question_data)), 200
