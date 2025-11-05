from flask import Blueprint, jsonify, request
from demo.utils.redis_own import RedisUtil

redis_demo_bp = Blueprint('redis_demo', __name__, url_prefix='/redis')

# 基础键值操作
@redis_demo_bp.route('/set', methods=['POST'])
def set_value():
    data = request.get_json()
    RedisUtil.set_key(data['key'], data['value'], ex=data.get('expire'))
    return jsonify({"status": "success"})

@redis_demo_bp.route('/get/<key>')
def get_value(key):
    value = RedisUtil.get_key(key)
    return jsonify({"key": key, "value": value})

# 队列操作
@redis_demo_bp.route('/queue/push', methods=['POST'])
def queue_push():
    data = request.get_json()
    RedisUtil.enqueue(data['queue'], data['item'])
    return jsonify({"status": "queued", "queue_length": RedisUtil.get_queue_length(data['queue'])})

@redis_demo_bp.route('/queue/pop/<queue_name>')
def queue_pop(queue_name):
    item = RedisUtil.dequeue(queue_name, timeout=5)
    return jsonify({"item": item} if item else {"status": "empty"})

# 计数器操作
@redis_demo_bp.route('/counter/incr/<key>')
def increment_counter(key):
    new_val = RedisUtil.incr_counter(key)
    return jsonify({"counter": key, "value": new_val})

# 调试用：查看所有键
@redis_demo_bp.route('/keys')
def list_keys():
    return jsonify({"keys": RedisUtil.get_all_keys()})
# 队列操作
@redis_demo_bp.route('/queue/lop', methods=['POST'])
def lop_push():
    data = request.get_json()
    RedisUtil.move_data_between_queues(data['queue'], data['other'])
    return jsonify({"status": "okk"})