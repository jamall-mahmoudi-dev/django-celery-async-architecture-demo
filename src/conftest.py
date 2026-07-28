import os

os.environ.setdefault("PYTEST_RUNNING", "1")

import pytest


@pytest.fixture(autouse=True)
def _celery_eager_and_locmem_email(settings):
    """
    Applied to every test automatically.

    CELERY_TASK_ALWAYS_EAGER=True makes .delay() execute the task
    synchronously in-process instead of requiring a real Redis broker
    and a running worker — appropriate for unit/integration tests
    where we want deterministic, fast results, not for testing Celery
    itself (that's what manual/E2E testing against the real stack is
    for, per the README).

    EMAIL_BACKEND=locmem captures sent emails in
    django.core.mail.outbox instead of hitting real SMTP — we don't
    want tests depending on smtp4dev being up.
    """
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
