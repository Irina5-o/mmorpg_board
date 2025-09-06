import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mmorpg_board.settings')

app = Celery('mmorpg_board')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send_weekly_messages': {
        'task': 'board.tasks.weekly_mailing',
        'schedule': crontab(day_of_week='sunday', hour='12', minute='00')
    }
}

app.conf.timezone = 'Europe/Moscow'
app.conf.broker_connection_retry_on_startup = True