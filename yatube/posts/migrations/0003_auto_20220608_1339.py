# Generated by Django 2.2.16 on 2022-06-08 10:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("posts", "0002_follow"),
    ]

    operations = [
        migrations.AlterField(
            model_name="follow",
            name="author",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="following",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Цель подписки",
            ),
        ),
        migrations.RemoveField(
            model_name="follow",
            name="user",
        ),
        migrations.AddField(
            model_name="follow",
            name="user",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="follower",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
