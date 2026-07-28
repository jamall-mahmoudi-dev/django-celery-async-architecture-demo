"""
Locust scenario for this demo.

Hits /api/register/ repeatedly with unique usernames — each request
creates a user AND dispatches a real Celery task, so this load test
exercises the whole chain: Nginx -> Gunicorn -> Django -> Redis ->
Celery worker -> smtp4dev, not just the HTTP layer in isolation.

Run against the dockerized stack (default host is nginx on :80):

    locust -f locustfile.py --host=http://localhost

Then open http://localhost:8089 for the Locust web UI and pick a
user count / spawn rate. For quick scenarios without the UI:

    locust -f locustfile.py --host=http://localhost \
        --users 100 --spawn-rate 10 --run-time 1m --headless
"""

import uuid

from locust import HttpUser, between, task


class RegisterUser(HttpUser):
    # Small pause between a simulated user's requests — avoids every
    # virtual user hammering register() in a tight loop, which would
    # test raw throughput rather than realistic usage.
    wait_time = between(0.5, 2.0)

    @task(3)
    def register(self):
        unique = uuid.uuid4().hex[:12]
        self.client.post(
            "/api/register/",
            json={
                "username": f"loadtest_{unique}",
                "email": f"loadtest_{unique}@example.com",
                "password": "supersecret123",
            },
            name="/api/register/",
        )

    @task(1)
    def check_random_task_status(self):
        # A made-up task_id most of the time — this deliberately also
        # exercises the "unknown task -> PENDING" path, not just the
        # happy path.
        self.client.get(
            f"/api/tasks/{uuid.uuid4()}/",
            name="/api/tasks/[id]/",
        )
