from django.urls import path

from notifications.views import RegisterView, TaskStatusView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("tasks/<str:task_id>/", TaskStatusView.as_view(), name="task-status"),
]
