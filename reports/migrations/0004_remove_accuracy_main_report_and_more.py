# Generated by Django 4.2 on 2024-09-30 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0003_alter_mainreport_confidence_level'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accuracy',
            name='main_report',
        ),
        migrations.AddField(
            model_name='accuracy',
            name='average_accuracy',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='accuracy',
            name='accuracy',
            field=models.FloatField(default=0),
        ),
    ]
