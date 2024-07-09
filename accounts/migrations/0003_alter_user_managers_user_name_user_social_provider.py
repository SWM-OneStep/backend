# Generated by Django 5.0.6 on 2024-07-05 08:42

import django.db.models.manager
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_created_at_user_deleted_at_user_updated_at_and_more'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('signup', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='name',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='social_provider',
            field=models.CharField(choices=[('GOOGLE', 'Google'), ('KAKAO', 'Kakao'), ('NAVER', 'Naver')], default='GOOGLE', max_length=30),
        ),
    ]