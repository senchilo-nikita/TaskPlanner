from django import forms
from django.contrib.auth import get_user_model

from .models import Task


class TaskForm(forms.ModelForm):
    due_date = forms.DateTimeField(
        label="Срок исполнения",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        input_formats=["%Y-%m-%dT%H:%M"],
    )

    class Meta:
        model = Task
        fields = ("title", "description", "priority", "due_date", "status", "assignee")
        labels = {
            "title": "Название задачи",
            "description": "Описание задачи",
            "priority": "Важность",
            "status": "Статус",
            "assignee": "Исполнитель",
        }

    def __init__(self, *args, user=None, friend_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        allowed_users = [user] + list(friend_choices or [])
        user_model = get_user_model()
        self.fields["assignee"].queryset = user_model.objects.filter(pk__in=[u.pk for u in allowed_users if u])
