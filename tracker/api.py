from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
from tracker.model import User
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




if __name__ == "__main__":
    app.run()