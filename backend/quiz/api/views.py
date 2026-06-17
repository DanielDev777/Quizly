from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

from quiz.models import Quiz, Question, Answer
from .serializers import (
    QuizListSerializer,
    QuizDetailSerializer,
    QuizCreateSerializer,
    QuizUpdateSerializer
)
from quiz.services.youtube_service import YouTubeTranscriptionService
from quiz.services.gemini_service import GeminiQuizGenerator

class QuizViewSet(viewsets.ModelViewSet):
    """ViewSet for Quiz CRUD operations."""
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        """Only return quizzes owned by authenticated user"""
        return Quiz.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return QuizCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return QuizUpdateSerializer
        elif self.action == 'list':
            return QuizListSerializer
        return QuizDetailSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create new quiz from YouTube URL.
        
        Process:
        1. Validate YouTube URL
        2. Download and transcribe video
        3. Generate quiz questions with AI
        4. Save quiz, questions, and answers to database
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        youtube_url = serializer.validated_data['youtube_url']
        title = serializer.validated_data.get('title')
        description = serializer.validated_data.get('description', '')

        try:
            youtube_service = YouTubeTranscriptionService(
                    whisper_model=settings.WHISPER_MODEL
                )
            result = youtube_service.process_youtube_video(youtube_url)

            gemini_service = GeminiQuizGenerator()
            questions_data = gemini_service.generate_quiz(transcription=result['transcription'])

            quiz = Quiz.objects.create(
                user=request.user,
                title=title,
                description=description,
                youtube_url=youtube_url,
                transcription=result['transcription']
            )

            for idx, q_data in enumerate(questions_data):
                question = Question.objects.create(
                    quiz=quiz,
                    question_text=q_data['question_title'],
                    order=idx
                )
                for ans_idx, option in enumerate(q_data['question_options']):
                    Answer.objects.create(
                        question=question,
                        answer_text=option,
                        is_correct=(option == q_data['answer']),
                        order=ans_idx
                    )

            return Response(
                QuizDetailSerializer(quiz).data,
                status=status.HTTP_201_CREATED
            )
        
        except Exception as e:
            return Response(
                {'error': f'Failed to create quiz: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    def update(self, request, *args, **kwargs):
        """Update quiz title and/or description only"""
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Delete quiz and all related questions/answers (CASCADE)"""
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)