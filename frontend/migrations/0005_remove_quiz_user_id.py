# Generated by Django 4.0.6 on 2022-07-17 04:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0004_remove_quiz_user_quiz_user_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quiz',
            name='user_id',
        ),
    ]
