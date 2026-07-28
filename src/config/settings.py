"""
Simple settings module — deliberately a single file (not split into
base/local/prod like the bigger project) because this project has
one purpose: demonstrate DRF + Celery + Redis + smtp4dev working
together. Every setting that matters for that story is env-driven so
the same code runs locally and in Docker without changes.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret-key-not-for-production")
DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third-party
    "rest_framework",
    "django_celery_results",
    # local
    "notifications",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ── Database ──────────────────────────────────────────────────────
# Postgres now (was SQLite) — Celery Beat's periodic cleanup task and
# Flower's task inspection are more representative of a real system
# once there's a real database behind django_celery_results.
#
# Exception: when PYTEST_RUNNING=1 (set at the top of conftest.py,
# before Django is configured), we fall back to an in-memory SQLite
# DB — so `pytest` still needs no running Postgres container, keeping
# the "tests don't need docker" promise from the README.
if os.environ.get("PYTEST_RUNNING") == "1":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB", "celery_drf_demo"),
            "USER": os.environ.get("POSTGRES_USER", "celery_drf_demo"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "changeme"),
            "HOST": os.environ.get("POSTGRES_HOST", "postgres"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── DRF ───────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
}

# ── Email — smtp4dev ──────────────────────────────────────────────
# smtp4dev is a fake SMTP server with no auth and no TLS — it exists
# purely to catch outgoing mail and show it in a web UI, so the
# EmailBackend config here is intentionally minimal.
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp4dev")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "25"))
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = "noreply@celery-drf-demo.local"

# ── Celery ────────────────────────────────────────────────────────
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
# django-db backend stores task results as rows in TaskResult
# (via django_celery_results), so we can expose a real "task status"
# DRF endpoint backed by the database instead of only Redis —
# demonstrates the pattern used for the Task Status API feature.
CELERY_RESULT_BACKEND = "django-db"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
# Retry settings applied per-task via @shared_task(...) instead of
# globally, so each task's retry policy is visible where the task is
# defined (see notifications/tasks.py).

# ── Celery Beat ───────────────────────────────────────────────────
# Static schedule (not django_celery_beat's DB-backed scheduler) —
# keeps this demo dependency-light: no extra admin-managed tables,
# the schedule is just visible right here in code. cleanup_old_task_results
# demonstrates the "Periodic Cleanup" pattern: TaskResult rows would
# grow unbounded otherwise.
CELERY_BEAT_SCHEDULE = {
    "cleanup-old-task-results-every-minute": {
        "task": "notifications.tasks.cleanup_old_task_results",
        "schedule": 60.0,  # seconds — frequent on purpose, so it's visible quickly in Flower/logs
    },
}
