from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from apps.accounts.models import User

from .models import FriendInvitation, Friendship


@login_required
def invite_friend(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        if email == request.user.email:
            messages.error(request, "Нельзя отправить приглашение самому себе.")
            return redirect("/?tab=friends")

        target = User.objects.filter(email=email, is_email_verified=True).first()
        if not target:
            messages.error(request, "Пользователь с таким email не найден или еще не подтвердил почту.")
            return redirect("/?tab=friends")

        if Friendship.objects.filter(user=request.user, friend=target).exists():
            messages.info(request, "Этот пользователь уже в списке друзей.")
            return redirect("/?tab=friends")

        reverse_invitation = FriendInvitation.objects.filter(
            sender=target,
            target=request.user,
            status=FriendInvitation.Status.PENDING,
        ).first()
        if reverse_invitation:
            messages.info(request, "У вас уже есть входящее приглашение от этого пользователя. Откройте его во вкладке друзей.")
            return redirect("/?tab=friends")

        invitation, created = FriendInvitation.objects.get_or_create(sender=request.user, target=target)
        if not created and invitation.status == FriendInvitation.Status.PENDING:
            messages.info(request, "Приглашение уже отправлено.")
        else:
            invitation.status = FriendInvitation.Status.PENDING
            invitation.save(update_fields=["status"])
            messages.success(request, "Приглашение отправлено.")
    return redirect("/?tab=friends")


@login_required
def accept_invitation(request, invitation_id):
    invitation = get_object_or_404(FriendInvitation, pk=invitation_id, target=request.user)
    if request.method == "POST" and invitation.status == FriendInvitation.Status.PENDING:
        invitation.status = FriendInvitation.Status.ACCEPTED
        invitation.save(update_fields=["status"])
        Friendship.objects.get_or_create(user=invitation.sender, friend=invitation.target)
        Friendship.objects.get_or_create(user=invitation.target, friend=invitation.sender)
        messages.success(request, "Приглашение принято.")
    return redirect("/?tab=friends")


@login_required
def decline_invitation(request, invitation_id):
    invitation = get_object_or_404(FriendInvitation, pk=invitation_id, target=request.user)
    if request.method == "POST" and invitation.status == FriendInvitation.Status.PENDING:
        invitation.status = FriendInvitation.Status.DECLINED
        invitation.save(update_fields=["status"])
        messages.info(request, "Приглашение отклонено.")
    return redirect("/?tab=friends")


@login_required
def update_friend_alias(request, friendship_id):
    friendship = get_object_or_404(Friendship, pk=friendship_id, user=request.user)
    if request.method == "POST":
        friendship.alias = request.POST.get("alias", "").strip()
        friendship.save(update_fields=["alias"])
        messages.success(request, "Имя друга обновлено.")
    return redirect("/?tab=friends")


@login_required
def delete_friendship(request, friendship_id):
    friendship = get_object_or_404(Friendship, pk=friendship_id, user=request.user)
    if request.method == "POST":
        friend = friendship.friend
        Friendship.objects.filter(user=request.user, friend=friend).delete()
        Friendship.objects.filter(user=friend, friend=request.user).delete()
        messages.success(request, "Друг удален.")
    return redirect("/?tab=friends")
