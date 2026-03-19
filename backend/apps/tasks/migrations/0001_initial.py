import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Task",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("due_date", models.DateTimeField()),
                ("priority", models.CharField(choices=[("low", "Низкая"), ("medium", "Средняя"), ("high", "Высокая"), ("critical", "Критическая")], default="medium", max_length=20)),
                ("status", models.CharField(choices=[("todo", "К выполнению"), ("in_progress", "В работе"), ("review", "На проверке"), ("done", "Выполнено")], default="todo", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("assignee", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="assigned_tasks", to="accounts.user")),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="created_tasks", to="accounts.user")),
            ],
            options={"ordering": ("due_date", "-created_at")},
        ),
    ]

