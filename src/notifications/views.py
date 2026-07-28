from celery.result import AsyncResult
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from config.celery import app as celery_app
from notifications.serializers import RegisterSerializer
from notifications.tasks import send_welcome_email


class RegisterView(APIView):
    """
    POST /api/register/

    Creates a user and dispatches send_welcome_email as a background
    Celery task. Returns immediately with the created user info and
    the Celery task_id — the response does NOT wait for the email to
    actually send. That's the whole point: check the returned task_id
    against /api/tasks/<task_id>/ to watch it move from PENDING to
    SUCCESS asynchronously.
    """

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        task = send_welcome_email.delay(user.email, user.username)

        return Response(
            {
                "user": {"id": user.id, "username": user.username, "email": user.email},
                "task_id": task.id,
                "task_status_url": f"/api/tasks/{task.id}/",
            },
            status=status.HTTP_201_CREATED,
        )


class TaskStatusView(APIView):
    """
    GET /api/tasks/<task_id>/

    Looks up a Celery task's current status via the configured result
    backend (django-db, see settings.CELERY_RESULT_BACKEND). This is
    the "Task Status API" pattern: polling this endpoint from the
    client is how you'd track long-running background work without
    websockets.
    """

    def get(self, request, task_id):
        result = AsyncResult(task_id, app=celery_app)

        response_data = {
            "task_id": task_id,
            "status": result.status,  # PENDING, STARTED, RETRY, SUCCESS, FAILURE
        }

        if result.successful():
            response_data["result"] = result.result
        elif result.failed():
            response_data["error"] = str(result.result)

        return Response(response_data)
