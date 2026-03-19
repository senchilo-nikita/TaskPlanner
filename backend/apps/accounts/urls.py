from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views


urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("verify/<uidb64>/<token>/", views.verify_email_view, name="verify_email"),
    path("password-reset/", views.password_reset_request_view, name="password_reset"),
    path("password-reset/<uidb64>/<token>/", views.password_reset_confirm_view, name="password_reset_confirm"),
]

