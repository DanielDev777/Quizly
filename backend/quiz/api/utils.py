from django.conf import settings
from quiz.models import Quiz, Question, Answer
from quiz.services.youtube_service import YouTubeTranscriptionService
from quiz.services.gemini_service import GeminiQuizGenerator


def build_quiz(user, youtube_url):
    """Orchestrate YouTube download, Whisper transcription, Gemini generation, and DB save."""
    yt_service = YouTubeTranscriptionService(whisper_model=settings.WHISPER_MODEL)
    result = yt_service.process_youtube_video(youtube_url)
    gemini_data = GeminiQuizGenerator().generate_quiz(result['transcription'])
    return save_quiz(user, youtube_url, result['transcription'], gemini_data)


def save_quiz(user, youtube_url, transcription, gemini_data):
    """Persist a quiz and all its questions to the database."""
    quiz = Quiz.objects.create(
        user=user,
        title=gemini_data['title'],
        description=gemini_data['description'],
        youtube_url=youtube_url,
        transcription=transcription,
    )
    for idx, q_data in enumerate(gemini_data['questions']):
        save_question(quiz, q_data, idx)
    return quiz


def save_question(quiz, q_data, idx):
    """Persist one question and its four answer choices to the database."""
    question = Question.objects.create(
        quiz=quiz,
        question_text=q_data['question_title'],
        order=idx,
    )
    for ans_idx, option in enumerate(q_data['question_options']):
        Answer.objects.create(
            question=question,
            answer_text=option,
            is_correct=(option == q_data['answer']),
            order=ans_idx,
        )
