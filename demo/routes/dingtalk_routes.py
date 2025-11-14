
from flask import Blueprint, request, jsonify
from demo.controller.dingtalk_controller import DingTalkController

dingtalk_bp = Blueprint('dingtalk', __name__, url_prefix='/dingtalk')

@dingtalk_bp.route('/send_report', methods=['POST'])
def send_report():
    """
    发送热点分析报告到钉钉

    请求参数：
    {
        "report_data": {
            "stats": [
                {
                    "word": "热点词汇",
                    "count": 10,
                    "titles": [
                        {
                            "title": "新闻标题",
                            "source_name": "新闻来源",
                            "ranks": [1, 3],
                            "rank_threshold": 10,
                            "url": "新闻链接",
                            "mobile_url": "移动端链接",
                            "time_display": "09:00",
                            "count": 2,
                            "is_new": true
                        }
                    ]
                }
            ],
            "new_titles": [],
            "failed_ids": []
        },
        "report_type": "当日汇总",
        "update_info": {
            "remote_version": "1.0.0",
            "current_version": "0.9.0"
        },
        "mode": "daily"
    }

    返回：
    {
        "code": 0,              # 0表示成功，-1表示失败
        "message": "操作结果信息",
        "data": {
            "message": "消息发送成功",
            "response": {}      # 钉钉API返回的原始数据
        }
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'code': -1,
                'message': '请求数据为空'
            }), 400

        report_data = data.get('report_data')
        report_type = data.get('report_type', '热点分析报告')
        update_info = data.get('update_info')
        mode = data.get('mode', 'daily')

        if not report_data:
            return jsonify({
                'code': -1,
                'message': '缺少report_data参数'
            }), 400

        # 发送钉钉消息
        result = DingTalkController.send_dingtalk_message(
            report_data=report_data,
            report_type=report_type,
            update_info=update_info,
            mode=mode
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'code': -1,
            'message': f'处理请求时出错: {str(e)}'
        }), 500

@dingtalk_bp.route('/test', methods=['GET'])
def test():
    """
    测试钉钉消息发送

    返回：
    {
        "code": 0,              # 0表示成功，-1表示失败
        "message": "操作结果信息",
        "data": {
            "message": "消息发送成功",
            "response": {}      # 钉钉API返回的原始数据
        }
    }
    """
    try:
        # 构造测试数据
        report_data = {
            'stats': [
                {
                    'word': '二狗日报2',
                    'count': 15,
                    'titles': [
                        {
                            'title': '昨夜二狗在王者十连跪是人性的溟灭',
                            'source_name': '科技新闻',
                            'ranks': [1, 3],
                            'rank_threshold': 10,
                            'url': 'http://example.com',
                            'mobile_url': '',
                            'time_display': '09:00',
                            'count': 2,
                            'is_new': True
                        }
                    ]
                }
            ],
            'new_titles': [],
            'failed_ids': []
        }

        # 发送测试消息
        result = DingTalkController.send_dingtalk_message(
            report_data=report_data,
            report_type='当日汇总'
        )

        # 直接返回结果，而不是再次jsonify
        return result

    except Exception as e:
        return jsonify({
            'code': -1,
            'message': f'测试请求时出错: {str(e)}'
        }), 500
