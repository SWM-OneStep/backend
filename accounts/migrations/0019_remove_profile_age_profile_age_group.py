# Generated by Django 4.2.16 on 2024-11-21 06:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0018_rename_user_profile_user_id_remove_profile_wake_time'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='age',
            new_name='age_group',
        ),
        migrations.AlterField(
            model_name='profile',
            name='age_group',
            field=models.CharField(choices=[('10', 'Teens'), ('20', 'Twenties'), ('30', 'Thirties'), ('40', 'Forties'), ('50', 'Fifties')], max_length=30),
        ),
    ]
