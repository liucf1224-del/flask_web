from flask import Blueprint, render_template

yolo_view_bp = Blueprint('yolo_view', __name__, url_prefix='/yolo')

@yolo_view_bp.route('/demo')
def yolo_demo():
    """
    YOLO演示页面
    """
    return render_template('yolo/yolo_demo.html')