from django.urls import path

from . import views


urlpatterns = [
    path("<int:task_id>/status/", views.update_task_status, name="update_task_status"),
]

