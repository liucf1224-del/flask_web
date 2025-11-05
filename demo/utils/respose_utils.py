# response_utils.py
from flask import jsonify

def success_response(data=None, message="操作成功", status_code=200):
    """
    成功响应
    :param data: 返回的数据
    :param message: 成功消息
    :param status_code: HTTP状态码
    :return: 响应对象
    """
    response = {
        "success": True,
        "message": message,
        "data": data
    }
    return jsonify(response), status_code

def error_response(message="操作失败", status_code=400, error_details=None):
    """
    错误响应
    :param message: 错误消息
    :param status_code: HTTP状态码
    :param error_details: 错误详情
    :return: 响应对象
    """
    response = {
        "success": False,
        "message": message,
        "error": error_details if error_details else message
    }
    return jsonify(response), status_code