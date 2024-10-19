from rest_framework import generics, permissions
from .models import Discussion
from .serializers import DiscussionSerializer
from .permissions import IsAdminUserOrReadOnly
from .tasks import generate_ai_comments

class DiscussionList(generics.ListCreateAPIView):
    queryset = Discussion.objects.all()
    serializer_class = DiscussionSerializer
    permission_classes = [IsAdminUserOrReadOnly]

    def perform_create(self, serializer):
        discussion = serializer.save(author=self.request.user)
        generate_ai_comments.delay(discussion.id)

class DiscussionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Discussion.objects.all()
    serializer_class = DiscussionSerializer
    permission_classes = [IsAdminUserOrReadOnly]