from django.contrib import admin
from django.urls import include, path

from apps.accounts.views import dashboard


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", dashboard, name="dashboard"),
    path("accounts/", include("apps.accounts.urls")),
    path("tasks/", include("apps.tasks.urls")),
    path("friends/", include("apps.friends.urls")),
]
