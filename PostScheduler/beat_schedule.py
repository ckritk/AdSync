from celery_app import app
from celery.schedules import crontab

app.conf.beat_schedule = {
    "check-every-minute": {
        "task": "tasks.check_and_post",
        "schedule": crontab(),  # every minute
    },
}
app.conf.timezone = 'UTC'
