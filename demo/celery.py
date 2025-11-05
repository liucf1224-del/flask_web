from celery import Celery

# celery = Celery('demo', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')
app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')