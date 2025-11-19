"""
易宝支付控制器
"""
from flask import Blueprint, request, jsonify
from ..utils.yeepay_client import YeepayClient
from ..utils.respose_utils import success_response, error_response
import uuid

yeepay_bp = Blueprint('yeepay', __name__, url_prefix='/yeepay')
yeepay_client = YeepayClient()


@yeepay_bp.route('/pay', methods=['POST'])
def create_payment():
    """
    创建支付订单
    """
    try:
        data = request.get_json()
        
        # 必需参数
        order_id = data.get('order_id') or str(uuid.uuid4())
        order_amount = data.get('order_amount')
        user_ip = data.get('user_ip')
        open_id = data.get('open_id')
        redirect_url = data.get('redirect_url')
        
        # 可选参数
        goods_name = data.get('goods_name', '充值')

        # 参数校验
        if not all([order_amount, user_ip, open_id, redirect_url]):
            return error_response("缺少必要参数: order_amount, user_ip, open_id, redirect_url")
        
        # 调用支付接口
        response = yeepay_client.create_payment(
            order_id=order_id,
            order_amount=order_amount,
            user_ip=user_ip,
            open_id=open_id,
            redirect_url=redirect_url,
            goods_name=goods_name
        )
        
        return success_response(data=response, message="支付订单创建成功")
        
    except Exception as e:
        return error_response(f"创建支付订单失败: {str(e)}")


@yeepay_bp.route('/query/<order_id>', methods=['GET'])
def query_payment(order_id):
    """
    查询支付结果
    """
    try:
        if not order_id:
            return error_response("缺少订单号")
            
        response = yeepay_client.query_payment(order_id)
        return success_response(data=response, message="查询成功")
        
    except Exception as e:
        return error_response(f"查询支付结果失败: {str(e)}")


@yeepay_bp.route('/refund', methods=['POST'])
def refund():
    """
    发起退款
    """
    try:
        data = request.get_json()
        
        # 必需参数
        order_id = data.get('order_id')
        refund_amount = data.get('refund_amount')
        refund_request_no = data.get('refund_request_no') or str(uuid.uuid4())
        
        # 参数校验
        if not all([order_id, refund_amount]):
            return error_response("缺少必要参数: order_id, refund_amount")
        
        # 调用退款接口
        response = yeepay_client.refund(
            order_id=order_id,
            refund_amount=refund_amount,
            refund_request_no=refund_request_no
        )
        
        return success_response(data=response, message="退款申请已提交")
        
    except Exception as e:
        return error_response(f"退款申请失败: {str(e)}")