from django.contrib.auth.hashers import make_password
from django.db import migrations


def create_default_test_user(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    email = "demo@taskplanner.local"
    password = "DemoPass123!"

    if not User.objects.filter(email=email).exists():
        user = User(
            email=email,
            username=email,
            first_name="Demo",
            last_name="User",
            is_active=True,
            is_email_verified=True,
            password=make_password(password),
        )
        user.save()


def remove_default_test_user(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    User.objects.filter(email="demo@taskplanner.local").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_default_test_user, remove_default_test_user),
    ]
