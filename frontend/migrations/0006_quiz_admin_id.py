# Generated by Django 4.0.6 on 2022-07-17 04:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0005_remove_quiz_user_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='admin_id',
            field=models.IntegerField(default=1),
        ),
    ]