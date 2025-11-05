# copyright_routes.py
from flask import Blueprint, request, current_app, jsonify
from demo import get_app_instance #引入实例
from demo.controller.copyright_controller import CopyrightController

copyright_bp = Blueprint('copyright', __name__, url_prefix='/copyrights')

# 修改后：
@copyright_bp.route('/export', methods=['GET'])
def export():
    # 正确获取并转换逗号分隔的ID字符串为整数列表
    id_str = request.args.get('facilitator_ids', '')
    if not id_str:
        return jsonify({"error": "Missing facilitator_ids parameter"}), 400

    try:
        facilitator_ids = [int(fid.strip()) for fid in id_str.split(',')]
    except ValueError:
        return jsonify({"error": "Invalid facilitator_ids format"}), 400
    app = get_app_instance()
    return CopyrightController.export(facilitator_ids, app=app)

@copyright_bp.route('/test', methods=['GET'])
def test():
    return jsonify({
        "app_name": current_app.name,  # ✅ 验证 current_app 是否可用
    })

# @copyright_bp.route('/export_demo', methods=['POST'])
# def export_demo():
#     data = request.get_json()
#     return CopyrightController.export_all_data(data)

