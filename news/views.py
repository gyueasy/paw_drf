
from django.shortcuts import render
from rest_framework import generics, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import NewsItem
from .serializers import NewsItemSerializer
from .tasks import analyze_with_openai

class NewsListView(generics.ListAPIView):
    queryset = NewsItem.objects.all().order_by('-published_date')
    serializer_class = NewsItemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['feed__name']
    search_fields = ['title', 'content', 'translated_title', 'translated_content']
    ordering_fields = ['published_date']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class NewsItemUpdateView(generics.UpdateAPIView):
    queryset = NewsItem.objects.all()
    serializer_class = NewsItemSerializer
    lookup_field = 'id'

    def perform_update(self, serializer):
        instance = serializer.save()
        analysis_result = analyze_with_openai(instance)
        if analysis_result:
            instance.ai_analysis = analysis_result
            instance.translated_title = analysis_result.get('translated_title', '')
            instance.translated_content = analysis_result.get('translated_content', '')
            instance.impact = analysis_result.get('impact', '')
            instance.tickers = ','.join(analysis_result.get('tickers', []))
            instance.save()