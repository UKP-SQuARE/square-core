from flask import Blueprint, jsonify, request

api = Blueprint("api", __name__)


@api.route("/test/<string:msg>", methods=["GET"])
def test_msg(msg):
    response = {"msg": "Your message was '{}'".format(msg)}
    return jsonify(response)
