from django.urls import path

from . import views


urlpatterns = [
    path("invite/", views.invite_friend, name="invite_friend"),
    path("invitation/<int:invitation_id>/accept/", views.accept_invitation, name="accept_invitation"),
    path("invitation/<int:invitation_id>/decline/", views.decline_invitation, name="decline_invitation"),
    path("friendship/<int:friendship_id>/alias/", views.update_friend_alias, name="update_friend_alias"),
    path("friendship/<int:friendship_id>/delete/", views.delete_friendship, name="delete_friendship"),
]
