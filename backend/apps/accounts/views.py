from collections import defaultdict
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Case, IntegerField, Value, When
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from apps.friends.models import FriendInvitation, Friendship
from apps.tasks.forms import TaskForm
from apps.tasks.models import Task

from .forms import LoginForm, PasswordResetConfirmAppForm, PasswordResetRequestForm, RegisterForm
from .models import User
from .tokens import email_verification_token

logger = logging.getLogger(__name__)


def build_absolute_link(request: HttpRequest, path: str) -> str:
    public_base_url = getattr(settings, "PUBLIC_BASE_URL", "") or settings.__dict__.get("PUBLIC_BASE_URL", "")
    if not public_base_url:
        public_base_url = request.build_absolute_uri("/").rstrip("/")
    else:
        public_base_url = public_base_url.rstrip("/")
    return f"{public_base_url}{path}"


def send_verification_email(request: HttpRequest, user: User) -> None:
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)
    verify_path = reverse("verify_email", kwargs={"uidb64": uid, "token": token})
    verify_url = build_absolute_link(request, verify_path)
    message = render_to_string("emails/verify_email.txt", {"user": user, "verify_url": verify_url})
    send_mail("Подтверждение регистрации", message, settings.DEFAULT_FROM_EMAIL, [user.email])


def send_password_reset_email(request: HttpRequest, user: User) -> None:
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_path = reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})
    reset_url = build_absolute_link(request, reset_path)
    message = render_to_string("emails/password_reset.txt", {"user": user, "reset_url": reset_url})
    send_mail("Сброс пароля", message, settings.DEFAULT_FROM_EMAIL, [user.email])


def register_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        try:
            send_verification_email(request, user)
        except Exception:
            logger.exception("Failed to send verification email for user %s", user.email)
            messages.error(request, "Аккаунт создан, но письмо подтверждения отправить не удалось. Проверьте настройки почты.")
        else:
            messages.success(request, "Регистрация завершена. Проверьте email для подтверждения аккаунта.")
        return redirect("login")
    return render(request, "accounts/register.html", {"form": form})


def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = LoginForm(request, request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        if not user.is_email_verified:
            try:
                send_verification_email(request, user)
            except Exception:
                logger.exception("Failed to resend verification email for user %s", user.email)
                messages.error(request, "Email не подтвержден, и письмо повторно отправить не удалось. Проверьте настройки почты.")
            else:
                messages.error(request, "Email не подтвержден. Мы отправили письмо повторно.")
            return redirect("login")
        login(request, user)
        return redirect("dashboard")
    return render(request, "accounts/login.html", {"form": form})


def verify_email_view(request: HttpRequest, uidb64: str, token: str) -> HttpResponse:
    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=user_id)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        user = None

    if user and email_verification_token.check_token(user, token):
        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])
        messages.success(request, "Email подтвержден. Теперь можно войти.")
    else:
        messages.error(request, "Ссылка подтверждения недействительна или устарела.")
    return redirect("login")


def password_reset_request_view(request: HttpRequest) -> HttpResponse:
    form = PasswordResetRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"].lower()
        user = User.objects.filter(email=email).first()
        if user:
            try:
                send_password_reset_email(request, user)
            except Exception:
                logger.exception("Failed to send password reset email for user %s", user.email)
                messages.error(request, "Не удалось отправить письмо для сброса пароля. Проверьте настройки почты.")
                return redirect("password_reset")
        messages.success(request, "Если пользователь существует, письмо для сброса пароля отправлено.")
        return redirect("login")
    return render(request, "accounts/password_reset_request.html", {"form": form})


def password_reset_confirm_view(request: HttpRequest, uidb64: str, token: str) -> HttpResponse:
    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=user_id)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        user = None

    if not user or not default_token_generator.check_token(user, token):
        messages.error(request, "Ссылка для сброса пароля недействительна или устарела.")
        return redirect("password_reset")

    form = PasswordResetConfirmAppForm(user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Пароль обновлен. Можно войти.")
        return redirect("login")
    return render(request, "accounts/password_reset_confirm.html", {"form": form})


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    tab = request.GET.get("tab", "tasks")

    friendships = Friendship.objects.filter(user=request.user).select_related("friend")
    friend_users = [friendship.friend for friendship in friendships]
    friend_labels = {
        friendship.friend_id: friendship.alias or friendship.friend.first_name or friendship.friend.email
        for friendship in friendships
    }

    task_form = TaskForm(user=request.user, friend_choices=friend_users)
    if request.method == "POST" and request.POST.get("action") == "create_task":
        task_form = TaskForm(request.POST, user=request.user, friend_choices=friend_users)
        if task_form.is_valid():
            task = task_form.save(commit=False)
            task.created_by = request.user
            task.save()
            messages.success(request, "Задача создана.")
            return redirect(f"{reverse('dashboard')}?tab=tasks")

    priority_rank = Case(
        When(priority=Task.Priority.CRITICAL, then=Value(1)),
        When(priority=Task.Priority.HIGH, then=Value(2)),
        When(priority=Task.Priority.MEDIUM, then=Value(3)),
        When(priority=Task.Priority.LOW, then=Value(4)),
        output_field=IntegerField(),
    )

    tasks = (
        Task.objects.filter_visible_for(request.user)
        .select_related("assignee", "created_by")
        .annotate(priority_rank=priority_rank)
        .order_by("due_date", "priority_rank", "-created_at")
    )
    kanban = defaultdict(list)
    for task in Task.objects.filter_visible_for(request.user).select_related("assignee", "created_by").order_by("due_date", "-created_at"):
        kanban[task.status].append(task)

    incoming_invitations = FriendInvitation.objects.filter(target=request.user, status=FriendInvitation.Status.PENDING).select_related("sender")
    outgoing_invitations = FriendInvitation.objects.filter(sender=request.user, status=FriendInvitation.Status.PENDING).select_related("target")

    context = {
        "tab": tab,
        "task_form": task_form,
        "tasks": tasks,
        "kanban": dict(kanban),
        "incoming_invitations": incoming_invitations,
        "outgoing_invitations": outgoing_invitations,
        "friendships": friendships,
        "friend_labels": friend_labels,
        "status_choices": Task.Status.choices,
        "priority_labels": dict(Task.Priority.choices),
    }
    return render(request, "dashboard.html", context)
