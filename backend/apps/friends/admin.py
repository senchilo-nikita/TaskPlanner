from django.contrib import admin

from .models import FriendInvitation, Friendship


@admin.register(FriendInvitation)
class FriendInvitationAdmin(admin.ModelAdmin):
    list_display = ("sender", "target", "status", "created_at")
    list_filter = ("status",)


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ("user", "friend", "created_at")

