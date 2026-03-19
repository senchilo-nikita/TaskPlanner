import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="FriendInvitation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("pending", "Ожидает"), ("accepted", "Принято"), ("declined", "Отклонено")], default="pending", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("sender", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="sent_friend_invitations", to="accounts.user")),
                ("target", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="received_friend_invitations", to="accounts.user")),
            ],
            options={"unique_together": {("sender", "target")}},
        ),
        migrations.CreateModel(
            name="Friendship",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("friend", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reverse_friendships", to="accounts.user")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="friendships", to="accounts.user")),
            ],
            options={"unique_together": {("user", "friend")}},
        ),
    ]

