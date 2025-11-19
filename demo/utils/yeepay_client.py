"""
易宝支付(Yeepay)客户端工具类
基于YOP Python SDK实现
"""
import os

from yop_python_sdk.auth.v3signer.credentials import YopCredentials
from yop_python_sdk.client.yopclient import YopClient

from ..setting import Config


class YeepayClient:
    def __init__(self):
        # 初始化客户端
        self.client = YopClient()
        self.merchant_no = Config.MERCHANT_NO
        self.app_key = Config.MERCHANT_APP_KEY
        self.private_key = Config.PRIMARY_KEY
        self.public_key = Config.PUBLIC_KEY
        self.app_id = Config.APP_ID

    def get_credentials(self):
        """
        获取认证信息
        """
        return YopCredentials(
            appKey=self.app_key,
            cert_type='RSA2048',
            priKey=self.private_key
        )

    def create_payment(self, order_id, order_amount, user_ip, open_id, redirect_url, goods_name="充值"):
        """
        发起支付请求

        :param order_id: 商户收款请求号
        :param order_amount: 订单金额
        :param user_ip: 用户真实IP地址
        :param open_id: 用户标识
        :param redirect_url: 回调地址
        :param goods_name: 商品名称
        :param app_id: 微信小程序/公众号appId
        :return: 支付结果
        """
        api = "/rest/v1.0/aggpay/pre-pay"
        params = {
            "payWay": "MINI_PROGRAM",
            "channel": "WECHAT",
            "goodsName": goods_name,
            "userIp": user_ip,
            "merchantNo": self.merchant_no,
            "orderId": order_id,
            "orderAmount": order_amount,
            "notifyUrl": redirect_url,
            "scene": "OFFLINE",
            "userId": open_id,
            "appId": self.app_id
        }

        credentials = self.get_credentials()
        response = self.client.post(api=api, post_params=params, credentials=credentials)
        return response

    def query_payment(self, order_id):
        """
        查询支付结果

        :param order_id: 商户收款请求号
        :return: 查询结果
        """
        api = "/rest/v1.0/trade/order/query"
        params = {
            "merchantNo": self.merchant_no,
            "orderId": order_id
        }

        credentials = self.get_credentials()
        response = self.client.get(api=api, query_params=params, credentials=credentials)
        return response

    def refund(self, order_id, refund_amount, refund_request_no):
        """
        发起退款请求

        :param order_id: 原始商户收款请求号,易宝的别的比如说易宝的或者银联的都可以就是3选1就是参数值不同
        :param refund_amount: 退款金额
        :param refund_request_no: 退款请求号
        :return: 退款结果
        """
        api = "/rest/v1.0/trade/refund"
        params = {
            "merchantNo": self.merchant_no,
            "orderId": order_id,
            "refundAmount": refund_amount,
            "refundRequestId": refund_request_no
        }

        credentials = self.get_credentials()
        response = self.client.post(api=api, post_params=params, credentials=credentials)
        return response