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
        # Routes the order processing task to the "orders" queue
        "app.tasks.process_order_task": {"queue": "orders"},
    },
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
)

# This allows the celery app to be run as a standalone script if needed.
if __name__ == "__main__":
    celery_app.start()
