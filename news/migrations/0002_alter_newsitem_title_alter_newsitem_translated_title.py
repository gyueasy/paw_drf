# Generated by Django 4.2 on 2024-10-19 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsitem',
            name='title',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='newsitem',
            name='translated_title',
            field=models.CharField(blank=True, max_length=500),
        ),
    ]
