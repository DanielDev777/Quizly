from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from quiz.models import Quiz
from .serializers import QuizSerializer, QuizCreateSerializer, QuizUpdateSerializer
from .utils import build_quiz


class QuizViewSet(viewsets.ModelViewSet):
    """ViewSet for Quiz CRUD operations."""
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        """Only return quizzes owned by the authenticated user."""
        return Quiz.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return QuizCreateSerializer
        if self.action in ['update', 'partial_update']:
            return QuizUpdateSerializer
        return QuizSerializer

    def create(self, request, *args, **kwargs):
        """POST /api/quizzes/ — create quiz from YouTube URL."""
        serializer = QuizCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            quiz = build_quiz(request.user, serializer.validated_data['url'])
            return Response(QuizSerializer(quiz).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """PATCH /api/quizzes/{id}/ — update title and/or description, return full quiz."""
        instance = self.get_object()
        serializer = QuizUpdateSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(QuizSerializer(instance).data)

    def destroy(self, request, *args, **kwargs):
        """DELETE /api/quizzes/{id}/ — permanently delete quiz."""
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
