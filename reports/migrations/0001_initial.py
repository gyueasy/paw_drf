# Generated by Django 4.2 on 2024-09-29 04:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChartReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_url', models.URLField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True, null=True)),
                ('technical_analysis', models.JSONField()),
                ('candlestick_analysis', models.JSONField()),
                ('moving_average_analysis', models.JSONField()),
                ('bollinger_bands_analysis', models.JSONField()),
                ('rsi_analysis', models.JSONField()),
                ('fibonacci_retracement_analysis', models.JSONField()),
                ('macd_analysis', models.JSONField()),
                ('support_resistance_analysis', models.JSONField()),
                ('overall_recommendation', models.CharField(blank=True, max_length=10, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MainReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('overall_analysis', models.TextField()),
                ('market_analysis', models.TextField()),
                ('chart_analysis', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('likers', models.ManyToManyField(related_name='liked_reports', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='NewsReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('news_analysis', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ReportWeights',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('overall_weight', models.FloatField(default=1.0)),
                ('market_weight', models.FloatField(default=1.0)),
                ('news_weight', models.FloatField(default=1.0)),
                ('chart_overall_weight', models.FloatField(default=1.0)),
                ('chart_technical_weight', models.FloatField(default=1.0)),
                ('chart_candlestick_weight', models.FloatField(default=1.0)),
                ('chart_moving_average_weight', models.FloatField(default=1.0)),
                ('chart_bollinger_bands_weight', models.FloatField(default=1.0)),
                ('chart_rsi_weight', models.FloatField(default=1.0)),
                ('chart_fibonacci_weight', models.FloatField(default=1.0)),
                ('chart_macd_weight', models.FloatField(default=1.0)),
                ('chart_support_resistance_weight', models.FloatField(default=1.0)),
                ('main_report', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='weights', to='reports.mainreport')),
            ],
        ),
    ]
