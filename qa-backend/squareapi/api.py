from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    JWTManager, jwt_required, jwt_optional, create_access_token,
    get_jwt_identity
)
from functools import wraps

from sqlalchemy import or_

from .models import db, User, Skill

api = Blueprint("api", __name__)
jwt = JWTManager()

@api.route("/register", methods=["POST"])
def register():
    username = request.json["username"]
    password = request.json["password"]
    user = User(username, password)
    db.session.add(user)
    db.session.commit()
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
def getSkills():
    user = get_jwt_identity()
    if user:
        skills = Skill.query.filter(or_(Skill.owner_id == user["id"], Skill.is_published.is_(True)))
    else:
        skills = Skill.query.filter(Skill.is_published.is_(True))
    return jsonify([s.to_dict() for s in skills]), 200

@api.route("/skill", methods=["POST"])
@jwt_required
def createSkill():
    skill_data = request.json["skill"]
    user = get_jwt_identity()
    skill = Skill(user=user, skill=skill_data)
    db.session.add(skill)
    db.session.commit()
    return jsonify(skill.to_dict()), 201

@api.route("/skill/<string:id>", methods=["POST"])
@jwt_required
def updateSkill(id):
    skill_data = request.json["skill"]
    user = get_jwt_identity()
    skill = Skill.query.filter_by(id=id).first()
    if not skill or skill.owner_id != user["id"]:
        return jsonify({"msg": "No skill found with id {}".format(id)}), 404
    skill.update(skill_data)
    db.session.commit()
    return jsonify(skill.to_dict()), 200

@api.route("/skill/<string:id>", methods=["DELETE"])
@jwt_required
def deleteSkill(id):
    user = get_jwt_identity()
    skill = Skill.query.filter_by(id=id).first()
    if not skill or skill.owner_id != user["id"]:
        return jsonify({"msg": "No skill found with id {}".format(id)}), 404
    skill.delete()
    db.session.commit()
    return jsonify(skill.to_dict()), 200

@api.route("/question", methods=["POST"])
def ask_question():
    question_data = request.json

    return jsonify([{"name": "CQA", "results":["Charles ate the french fries knowing they would be his last meal.",
                             "She had a habit of taking showers in lemonade.",
                             "I would be delighted if the sea were full of cucumber juice."]},
                    {"name": "KQA", "results": ["This book is sure to liquefy your brain.",
                             "Wisdom is easily acquired when hiding under the bed with a saucepan on your head."]}]), 200