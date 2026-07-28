"""
Celery tasks for the notifications app.

send_welcome_email is the centerpiece of this demo project: it's a
real task that sends a real email over SMTP to smtp4dev, with a
retry policy — not a toy `add(x, y)` task. This is what makes the
Celery + Redis + smtp4dev chain worth looking at.
"""

import logging

from celery import shared_task
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,  # seconds between retries
    autoretry_for=(Exception,),
    retry_backoff=True,  # exponential backoff: 10s, 20s, 40s...
    retry_backoff_max=60,
    retry_jitter=True,
)
def send_welcome_email(self, user_email: str, username: str) -> str:
    """
    Sends a welcome email to a newly registered user.

    Runs async via Celery so the DRF registration endpoint returns
    immediately without waiting on SMTP. Retries automatically on
    any exception (e.g. smtp4dev being temporarily unreachable),
    with exponential backoff — this is the "Retry Mechanism" feature
    demonstrated concretely, not just described.
    """
    logger.info("Sending welcome email to %s (attempt %s)", user_email, self.request.retries + 1)

    send_mail(
        subject="Welcome to Celery/DRF Demo!",
        message=(
            f"Hi {username},\n\n"
            "Your registration was received and this email was sent "
            "asynchronously by a Celery worker, routed through Redis, "
            "delivered via smtp4dev.\n\n"
            "You can inspect this email in the smtp4dev web UI."
        ),
        from_email=None,  # falls back to DEFAULT_FROM_EMAIL
        recipient_list=[user_email],
        fail_silently=False,
    )

    logger.info("Welcome email sent to %s", user_email)
    return f"welcome email sent to {user_email}"


@shared_task
def cleanup_old_task_results(max_age_hours: int = 1) -> str:
    """
    Deletes TaskResult rows older than max_age_hours.

    Run periodically by Celery Beat (see settings.CELERY_BEAT_SCHEDULE).
    Without this, django_celery_results' TaskResult table grows
    without bound — every task run (register calls, this cleanup task
    itself) leaves a row. This is the "Periodic Cleanup" feature made
    concrete: a scheduled task that keeps the system healthy on its
    own, with no manual intervention.
    """
    from datetime import timedelta

    from django.utils import timezone
    from django_celery_results.models import TaskResult

    cutoff = timezone.now() - timedelta(hours=max_age_hours)
    deleted_count, _ = TaskResult.objects.filter(date_done__lt=cutoff).delete()

    logger.info("cleanup_old_task_results: deleted %s old TaskResult rows", deleted_count)
    return f"deleted {deleted_count} old task results"
