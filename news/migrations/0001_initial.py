# Generated by Django 4.2 on 2024-10-19 08:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('url', models.URLField(unique=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='NewsItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('published_date', models.DateTimeField()),
                ('link', models.URLField()),
                ('translated_title', models.CharField(blank=True, max_length=200)),
                ('translated_content', models.TextField(blank=True)),
                ('impact', models.CharField(blank=True, max_length=50)),
                ('tickers', models.CharField(blank=True, max_length=100)),
                ('image_url', models.URLField(blank=True, null=True)),
                ('ai_analysis', models.JSONField(blank=True, null=True)),
                ('feed', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='news_items', to='news.news')),
            ],
        ),
    ]
