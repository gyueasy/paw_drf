# Generated by Django 4.2 on 2024-09-30 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0002_alter_mainreport_recommendation_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mainreport',
            name='confidence_level',
            field=models.TextField(blank=True, null=True),
        ),
    ]
