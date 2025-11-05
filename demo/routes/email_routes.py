from flask import Blueprint
from demo.utils.email import send_email

email_bp = Blueprint('email', __name__)

@email_bp.route('/test-email', methods=['GET'])
def test_email():
    print('test email')
    # 发送测试邮件
    send_email(
        subject='发送测试',
        recipients=['1967963174@qq.com'],  # 替换为实际邮箱
        text_body='这是一封测试邮件',
        html_body='<h1>HTML内容测试</h1><p>邮件发送成功！</p>'
    )
    return '测试邮件已发送，请检查收件箱（包括垃圾邮件箱）'