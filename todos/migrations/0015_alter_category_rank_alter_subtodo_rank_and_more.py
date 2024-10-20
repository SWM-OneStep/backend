# Generated by Django 4.2.16 on 2024-10-11 06:18

from django.db import migrations
import django_lexorank.fields


class Migration(migrations.Migration):

    dependencies = [
        ('todos', '0014_rename_order_category_rank_rename_order_subtodo_rank_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='rank',
            field=django_lexorank.fields.RankField(db_index=True, editable=False, max_length=255),
        ),
        migrations.AlterField(
            model_name='subtodo',
            name='rank',
            field=django_lexorank.fields.RankField(db_index=True, editable=False, max_length=255),
        ),
        migrations.AlterField(
            model_name='todo',
            name='rank',
            field=django_lexorank.fields.RankField(db_index=True, editable=False, max_length=255),
        ),
    ]