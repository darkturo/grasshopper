from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token, get_jwt_identity, jwt_required
)
from grasshopper.tracker.model.user import User
from grasshopper.tracker.model.testrun import TestRun
from uuid import UUID

bp = Blueprint('v1', __name__, url_prefix='/v1/api')


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
    return jsonify(token=access_token), 200


@bp.route("/testrun", methods=["POST"])
@jwt_required()
def testrun():
    current_user = get_jwt_identity()

    user = User.find_by_username(current_user)
    res = TestRun.create(user.id,
                         request.json.get("name"),
                         request.json.get("description"),
                         request.json.get("threshold"))

    return jsonify(id=UUID(bytes=res['id']), start_time=res['start_time']), 201


@bp.route("/testrun/<testrun_id>/usage", methods=["POST"])
@jwt_required()
def testrun_record_usage(testrun_id):
    current_user = get_jwt_identity()

    user = User.find_by_username(current_user)
    test_run = TestRun.find_by_id(testrun_id)
    if not test_run:
        return jsonify({"msg": "No testrun found"}), 404

    if test_run.user_id != user.id:
        return jsonify({"msg": "Forbidden"}), 403

    try:
        usage = float(request.json.get("usage"))
    except ValueError:
        return jsonify({"msg": "Invalid usage value"}), 400

    test_run.record_cpu_usage(usage)
    return jsonify({"msg": "Usage recorded"}, 201)


@bp.route("/testrun/<testrun_id>/stop", methods=["POST"])
@jwt_required()
def testrun_stop(testrun_id):
    current_user = get_jwt_identity()

    user = User.find_by_username(current_user)
    print(f"BACKEND: {testrun_id}")
    test_run = TestRun.find_by_id(testrun_id)
    print(f"BACKEND: {test_run}")
    if not test_run:
        return jsonify({"msg": "No testrun found"}), 404

    if test_run.user_id != user.id:
        return jsonify({"msg": "Forbidden"}), 403

    test_run.finish()
    return jsonify({"msg": "Testrun finished"}), 200


@bp.route("/testrun/<testrun_id>", methods=["GET"])
@jwt_required()
def testrun_get(testrun_id):
    current_user = get_jwt_identity()

    user = User.find_by_username(current_user)
    test_run = TestRun.find_by_id(testrun_id)
    if not test_run:
        return jsonify({"msg": "No testrun found"}), 404

    if test_run.user_id != user.id:
        return jsonify({"msg": "Forbidden"}), 403

    stats = test_run.get_test_execution_stats()
    return jsonify(id=test_run.id,
                   time_above_threshold=stats["time_above_threshold"],
                   start_time=test_run.start_time,
                   end_time=test_run.end_time,
                   duration=stats["duration"]), 200
