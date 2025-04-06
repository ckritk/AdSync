from celery import Celery
app = Celery("post_scheduler", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0")
