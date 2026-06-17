from rest_framework import serializers
from quiz.models import Quiz, Question, Answer

class AnswerSerializer(serializers.ModelSerializer):
    """Serializer for answer choices"""
    class Meta:
        model = Answer
        fields = ['id', 'answer_text', 'is_correct', 'order']
        read_only_fields = ['id']

class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for questions with nested answers"""
    answers = AnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'difficulty', 'order', 'answers']
        read_only_fields = ['id']

class QuizListSerializer(serializers.ModelSerializer):
    """Serializer for quiz list view (lighter payload, no full questions)"""
    question_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'youtube_url',
            'question_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_question_count(self, obj):
        return obj.questions.count()
    
class QuizDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed quiz view with all questions"""
    questions = QuestionSerializer(many=True, read_only=True)
    question_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = (
            'id', 'title', 'description', 'youtube_url',
            'transcription', 'questions', 'question_count',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'transcription')
    
    def get_question_count(self, obj):
        return obj.questions.count()
    
class QuizCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new quiz from YouTube URL"""
    class Meta:
        model = Quiz
        fields = ('youtube_url', 'title', 'description')

    def validate_youtube_url(self, value):
        youtube_patterns = ['youtube.com', 'youtu.be', 'youtube-nocookie.com', 'm.youtube.com']
        if not any(pattern in value for pattern in youtube_patterns):
            raise serializers.ValidationError("Must be a valid YouTube URL")
        return value
    
class QuizUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating quiz metadata only"""
    class Meta:
        model = Quiz
        fields = ('title', 'description')