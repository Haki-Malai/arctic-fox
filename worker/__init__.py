from api import celery, create_app

app = create_app()
app.app_context().push()

celery.conf.task_routes = {
    'worker.tasks.*': {'queue': 'worker'},
}
celery.autodiscover_tasks(['worker.tasks'], force=True)
