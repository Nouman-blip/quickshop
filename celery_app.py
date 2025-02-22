# celery_app.py

from celery import Celery

# Initialize the Celery application
celery_app = Celery(
    "quickshop",
    broker="redis://localhost:6379/0",   # Redis as message broker
    backend="redis://localhost:6379/0"   # Redis as result backend
)

# Update Celery configuration settings
celery_app.conf.update(
    task_routes={
        "app.tasks.process_order_task": {"queue": "orders"},
    },
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    # Add beat schedule if needed
    beat_schedule={
        'generate-daily-reports': {
            'task': 'app.tasks.generate_periodic_reports',
            'schedule': crontab(hour=0, minute=0),  # Run daily at midnight
        },
    }
    task_acks_late=True,  # Tasks are acknowledged after completion
    task_reject_on_worker_lost=True,  # Reject tasks if worker disconnects
    task_time_limit=3600,  # Task timeout in seconds
)

# This allows the celery app to be run as a standalone script if needed.
if __name__ == "__main__":
    celery_app.start()
