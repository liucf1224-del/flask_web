# auth_routes.py
from flask import Blueprint, request, jsonify
from ..controller.auth_controller import AuthController
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(force=True)
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"error": "用户名和密码不能为空"}), 400

    return AuthController.check_user(username, password)