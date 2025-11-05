# D:\new\demo\server\task_server.py
from demo import celery
import time

from demo.utils.email import send_email


@celery.task()
def long_running_task(seconds):
    """
    模拟一个长时间运行的任务
    """
    time.sleep(seconds)
    return f"任务已完成，耗时 {seconds} 秒"

@celery.task()
def send_email_task(email=None, message=None):
    """
    模拟发送电子邮件的任务，并返回可查询的状态信息
    """
    try:
        # 如果未传入 email，则使用默认值
        recipient = email if email else '2214305959@qq.com'
        content = message if message else '这是一封测试邮件'

        send_email(
            subject='发送测试',
            recipients=[recipient],
            text_body=content,
            html_body=f'<h1>HTML内容测试</h1><p>{content}</p>'
        )
        return {
            "status": "success",
            "message": f"邮件已成功发送至 {recipient}"
        }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }
