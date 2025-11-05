# user_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from demo.controller.user_controller import UserController

user_bp = Blueprint('user', __name__, url_prefix='/users')


@user_bp.route('/list', methods=['GET'])
@jwt_required()
def get_users():
    jwt_payload = get_jwt()  # 获取 JWT 的 payload 部分
    current_user = get_jwt_identity()  # 获取 identity 值，比如 username 或 user_id
    print(jwt_payload)
    print(current_user)
    return UserController.get_all_users()

@user_bp.route('/add', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')

    if not username or not email:
        return jsonify({"error": "用户名和邮箱不能为空"}), 400

    return UserController.create_user(username, email)

@user_bp.route('/edit', methods=['POST'])
def edit_user():
    data = request.get_json()
    username = data.get('username')
    id = data.get('id')
    email = data.get('email')

    if not username or not email:
        return jsonify({"error": "用户名和邮箱不能为空"}), 400
    return UserController.edit_user(username, email,id)

@user_bp.route('/delete', methods=['DELETE'])
def delete_user():
    data = request.get_json()
    id = data.get('id')
    return  UserController.delete_user(id)