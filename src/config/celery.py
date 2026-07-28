"""
Celery application entry point.

This module creates the Celery app and tells it to pull config from
Django settings (any CELERY_* setting in settings.py) and to
auto-discover tasks.py in every installed app. Imported from
config/__init__.py so `from config.celery import app as celery_app`
runs whenever Django starts — this is what makes `@shared_task`
decorators in notifications/tasks.py work without manual wiring.
"""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("celery_drf_demo")

# Read CELERY_* keys from Django settings.py (namespace="CELERY"
# means we write CELERY_BROKER_URL, not just BROKER_URL).
app.config_from_object("django.conf:settings", namespace="CELERY")

# Look for a tasks.py in every app listed in INSTALLED_APPS.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """Trivial task used only to sanity-check the Celery wiring."""
    print(f"Request: {self.request!r}")
