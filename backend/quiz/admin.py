from django.contrib import admin
from quiz.models import Quiz, Question, Answer

class AnswerInline(admin.TabularInline):
    """Display answers inline within question form"""
    model = Answer
    extra = 4
    fields = ('answer_text', 'is_correct', 'order')


class QuestionInline(admin.StackedInline):
    """Display questions inline within quiz form"""
    model = Question
    extra = 0
    show_change_link = True
    fields = ('question_text', 'difficulty', 'order')


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'question_count', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('title', 'youtube_url')
    readonly_fields = ('created_at', 'updated_at', 'transcription')
    inlines = [QuestionInline]
    
    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = 'Questions'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text_short', 'quiz', 'difficulty', 'order')
    list_filter = ('difficulty', 'quiz')
    search_fields = ('question_text',)
    inlines = [AnswerInline]
    
    def question_text_short(self, obj):
        return obj.question_text[:75] + '...' if len(obj.question_text) > 75 else obj.question_text
    question_text_short.short_description = 'Question'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('answer_text', 'question', 'is_correct', 'order')
    list_filter = ('is_correct', 'question__quiz')
    search_fields = ('answer_text',)