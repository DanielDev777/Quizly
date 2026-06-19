from rest_framework import serializers
from quiz.models import Quiz, Question, Answer
from quiz.services.youtube_service import get_youtube_embed_url


class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for a question in the spec format:
    { id, question_title, question_options: [...], answer: "correct text" }
    """
    question_title = serializers.CharField(source='question_text')
    question_options = serializers.SerializerMethodField()
    answer = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'question_title', 'question_options', 'answer', 'created_at', 'updated_at']

    def get_question_options(self, obj):
        """Return all answer texts as a plain list of strings."""
        return list(obj.answers.values_list('answer_text', flat=True))

    def get_answer(self, obj):
        """Return the text of the correct answer."""
        correct = obj.answers.filter(is_correct=True).first()
        return correct.answer_text if correct else None


class QuizSerializer(serializers.ModelSerializer):
    """
    Full quiz serializer matching the spec response shape:
    { id, title, description, created_at, updated_at, video_url, questions: [...] }
    """
    video_url = serializers.SerializerMethodField()
    questions = QuestionSerializer(many=True, read_only=True)

    def get_video_url(self, obj):
        """Return the YouTube embed URL derived from the stored video URL."""
        return get_youtube_embed_url(obj.youtube_url)

    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description',
            'created_at', 'updated_at',
            'video_url', 'questions',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class QuizCreateSerializer(serializers.Serializer):
    """
    Serializer for POST /api/quizzes/.
    Spec expects { url } not { youtube_url }.
    """
    url = serializers.URLField()

    def validate_url(self, value):
        youtube_patterns = [
            'youtube.com', 'youtu.be',
            'youtube-nocookie.com', 'm.youtube.com',
        ]
        if not any(pattern in value for pattern in youtube_patterns):
            raise serializers.ValidationError("Must be a valid YouTube URL.")
        return value


class QuizUpdateSerializer(serializers.ModelSerializer):
    """Serializer for PATCH /api/quizzes/{id}/ — title and description only."""
    class Meta:
        model = Quiz
        fields = ('title', 'description')