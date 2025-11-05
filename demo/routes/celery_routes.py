# D:\new\demo\routes\celery_routes.py
from flask import Blueprint, request, jsonify

from demo import celery
from demo.server.task_server import long_running_task, send_email_task
from celery.result import AsyncResult

bp = Blueprint('celery', __name__)

@bp.route('/start-task', methods=['POST'])
def start_task():
    seconds = int(request.json.get('seconds', 5))
    task = long_running_task.delay(seconds)
    return jsonify({"task_id": task.id}), 202

@bp.route('/send-email', methods=['POST'])
def send_email():
    email = request.json.get('email')
    message = request.json.get('message')
    if not email or not message:
        return jsonify({"error": "缺少必要参数"}), 400
    task = send_email_task.delay(email=email, message=message)
    return jsonify({"task_id": task.id}), 202

@bp.route('/task-status/<task_id>', methods=['GET'])
def task_status(task_id):

    task_result = AsyncResult(task_id, app=celery)
    return jsonify({
        "task_id": task_id,
        "status": task_result.state,
        "result": task_result.result
    })
