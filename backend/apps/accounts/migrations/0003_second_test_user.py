from django.contrib.auth.hashers import make_password
from django.db import migrations


def create_second_test_user(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    email = "friend@taskplanner.local"
    password = "FriendPass123!"

    if not User.objects.filter(email=email).exists():
        User.objects.create(
            email=email,
            username=email,
            first_name="Friend",
            last_name="User",
            is_active=True,
            is_email_verified=True,
            password=make_password(password),
        )


def remove_second_test_user(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    User.objects.filter(email="friend@taskplanner.local").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_default_test_user"),
    ]

    operations = [
        migrations.RunPython(create_second_test_user, remove_second_test_user),
    ]

