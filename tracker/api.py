from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
from tracker.model import User, TestRun
bp = Blueprint('api-v1', __name__, url_prefix='/v1/api')
jwt = JWTManager(current_app)


@bp.route("/auth", methods=["POST"])
def auth():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    user = User.find_by_username(username)
    if not user:
        return jsonify({"msg": "No user found"}), 404

    if not user.check_password(password):
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(token=access_token)


@app.route("/testrun", methods=["POST"])
@jwt_required()
def testrun():
    current_user = get_jwt_identity()

    user = User.find_by_username(current_user)
    test_run = TestRun.create(user.id,
                   request.json.get("name"),
                   request.json.get("description"),
                   request.json.get("threshold"))
    return jsonify(id=test_run.id, start_time=test_run.start_time)


if __name__ == "__main__":
    app.run()