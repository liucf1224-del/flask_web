# utils/email.py
from flask import current_app
from flask_mail import Message
from threading import Thread
from .extensions import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(  subject, recipients, text_body, html_body=None, attachments=None):
    """发送邮件

    Args:
        subject: 邮件主题
        recipients: 收件人列表数组
        text_body: 纯文本正文
        html_body: HTML正文(可选)
        attachments: 附件列表，每个附件是(filename, content_type, data)元组
    """
    msg = Message(subject, recipients=recipients)
    msg.body = text_body
    if html_body:
        msg.html = html_body

    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)

    # 异步发送邮件
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()