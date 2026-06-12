from django.test import TestCase
from django.contrib.auth import get_user_model
from quiz.models import Quiz, Question, Answer
import uuid

User = get_user_model()

class QuizModelTests(TestCase):
    """Test cases for Quiz models"""
    
    def setUp(self):
        """Create test user for quiz creation"""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!'
        )
    
    def test_create_quiz(self):
        """Test creating a quiz"""
        quiz = Quiz.objects.create(
            user=self.user,
            title='Test Quiz',
            description='Test Description',
            youtube_url='https://www.youtube.com/watch?v=test',
            transcription='Test transcription'
        )
        
        self.assertEqual(quiz.title, 'Test Quiz')
        self.assertEqual(quiz.user, self.user)
        self.assertIsInstance(quiz.id, uuid.UUID)
        self.assertIn('Test Quiz', str(quiz))
    
    def test_quiz_cascade_delete(self):
        """Test that deleting user deletes their quizzes"""
        quiz = Quiz.objects.create(
            user=self.user,
            title='Test Quiz',
            youtube_url='https://www.youtube.com/watch?v=test'
        )
        
        quiz_id = quiz.id
        self.user.delete()
        
        self.assertFalse(Quiz.objects.filter(id=quiz_id).exists())
    
    def test_create_question(self):
        """Test creating a question"""
        quiz = Quiz.objects.create(
            user=self.user,
            title='Test Quiz',
            youtube_url='https://www.youtube.com/watch?v=test'
        )
        
        question = Question.objects.create(
            quiz=quiz,
            question_text='What is Python?',
            difficulty='medium',
            order=0
        )
        
        self.assertEqual(question.quiz, quiz)
        self.assertEqual(question.difficulty, 'medium')
        self.assertEqual(quiz.questions.count(), 1)
    
    def test_create_answer(self):
        """Test creating answers for a question"""
        quiz = Quiz.objects.create(
            user=self.user,
            title='Test Quiz',
            youtube_url='https://www.youtube.com/watch?v=test'
        )
        
        question = Question.objects.create(
            quiz=quiz,
            question_text='What is Python?',
            order=0
        )
        
        answer1 = Answer.objects.create(
            question=question,
            answer_text='A programming language',
            is_correct=True,
            order=0
        )
        
        answer2 = Answer.objects.create(
            question=question,
            answer_text='A snake',
            is_correct=False,
            order=1
        )
        
        self.assertEqual(question.answers.count(), 2)
        self.assertTrue(answer1.is_correct)
        self.assertFalse(answer2.is_correct)
    
    def test_question_cascade_delete(self):
        """Test that deleting quiz deletes questions and answers"""
        quiz = Quiz.objects.create(
            user=self.user,
            title='Test Quiz',
            youtube_url='https://www.youtube.com/watch?v=test'
        )
        
        question = Question.objects.create(
            quiz=quiz,
            question_text='Test?',
            order=0
        )
        
        Answer.objects.create(
            question=question,
            answer_text='Answer 1',
            is_correct=True,
            order=0
        )
        
        question_id = question.id
        quiz.delete()
        
        # Question and answers should be deleted
        self.assertFalse(Question.objects.filter(id=question_id).exists())
        self.assertEqual(Answer.objects.count(), 0)