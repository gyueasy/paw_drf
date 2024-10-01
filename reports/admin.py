from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget
from .models import ChartReport, NewsReport, MainReport, ReportWeights, Price, Accuracy

@admin.register(ChartReport)
class ChartReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'overall_recommendation')
    list_display_links = ('id', 'timestamp')
    list_filter = ('overall_recommendation',)
    search_fields = ('overall_recommendation',)
    list_editable = ('overall_recommendation',)
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }

@admin.register(NewsReport)
class NewsReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
    list_display_links = ('id', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('news_analysis',)

@admin.register(MainReport)
class MainReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'recommendation', 'confidence_level', 'created_at')
    list_display_links = ('id', 'title')
    list_filter = ('recommendation', 'confidence_level', 'created_at')
    search_fields = ('title', 'recommendation', 'reasoning')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ReportWeights)
class ReportWeightsAdmin(admin.ModelAdmin):
    list_display = ('id', 'main_report', 'overall_weight', 'created_at')
    list_display_links = ('id', 'main_report')
    list_filter = ('created_at',)
    search_fields = ('main_report__title', 'reasoning')

@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ('id', 'market', 'trade_price', 'timestamp')
    list_display_links = ('id', 'market')
    list_filter = ('market', 'timestamp')
    search_fields = ('market',)

@admin.register(Accuracy)
class AccuracyAdmin(admin.ModelAdmin):
    list_display = ('id', 'accuracy', 'average_accuracy_percent', 'recommendation', 'recommendation_value', 'price_change_percent', 'is_correct', 'calculated_at')
    list_filter = ('calculated_at', 'recommendation', 'is_correct')
    search_fields = ('accuracy', 'average_accuracy', 'recommendation')

    def average_accuracy_percent(self, obj):
        return f"{obj.average_accuracy:.2f}%"
    average_accuracy_percent.short_description = 'Avg Accuracy (%)'

    def price_change_percent(self, obj):
        return f"{obj.price_change:.2f}%"
    price_change_percent.short_description = 'Price Change (%)'