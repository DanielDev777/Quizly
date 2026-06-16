from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from quiz.models import Quiz, Question, Answer

User = get_user_model()

class QuizAPITests(APITestCase):
    """Test Quiz CRUD endpoints"""

    def setUp(self):
        """Create test user and authenticate"""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!'
        )
        self.client.force_authenticate(user=self.user)

    def test_list_quizzes_authenticated(self):
        """Test listing quizzes requires authentication"""
        self.client.force_authenticate(user=None)
        url = reverse('quiz-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_user_quizzes(self):
        """Test user can list their own quizzes"""

        quiz = Quiz.objects.create(
            user=self.user,
            title='My Quiz',
            youtube_url='https://youtube.com/watch?v=test'
        )

        url = reverse('quiz-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'My Quiz')

    def test_user_cannot_see_other_users_quizzes(self):
        """Test user isolation - cannot see others' quizzes"""
        other_user = User.objects.create_user(
            email='other@example.com',
            username='otheruser',
            password='TestPass123!'
        )
        
        Quiz.objects.create(
            user=other_user,
            title='Other Quiz',
            youtube_url='https://youtube.com/watch?v=test'
        )
        
        url = reverse('quiz-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    @patch('quiz.api.views.YouTubeTranscriptionService')
    @patch('quiz.api.views.GeminiQuizGenerator')
    def test_create_quiz_from_youtube_url(self, mock_gemini, mock_youtube):
        """Test creating quiz from YouTube URL"""
        mock_yt_instance = MagicMock()
        mock_yt_instance.process_youtube_video.return_value = {
            'transcription': 'Test transcription',
            'language': 'en',
        }
        mock_youtube.return_value = mock_yt_instance
        
        # Mock Gemini service
        mock_gemini_instance = MagicMock()
        mock_gemini_instance.generate_quiz.return_value = [
            {
                'question_text': 'What is this?',
                'difficulty': 'medium',
                'answers': [
                    {'answer_text': 'A', 'is_correct': True},
                    {'answer_text': 'B', 'is_correct': False},
                    {'answer_text': 'C', 'is_correct': False},
                    {'answer_text': 'D', 'is_correct': False}
                ]
            }
        ]
        mock_gemini.return_value = mock_gemini_instance
        
        url = reverse('quiz-list')
        data = {
            'youtube_url': 'https://youtube.com/watch?v=test',
            'title': 'My Test Quiz'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'My Test Quiz')
        self.assertEqual(len(response.data['questions']), 1)
    
    def test_retrieve_quiz_detail(self):
        """Test retrieving quiz with all questions"""
        quiz = Quiz.objects.create(
            user=self.user,
            title='My Quiz',
            youtube_url='https://youtube.com/watch?v=test'
        )
        
        question = Question.objects.create(
            quiz=quiz,
            question_text='Test?',
            order=0
        )
        
        Answer.objects.create(
            question=question,
            answer_text='Answer A',
            is_correct=True,
            order=0
        )
        
        url = reverse('quiz-detail', kwargs={'pk': quiz.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'My Quiz')
        self.assertEqual(len(response.data['questions']), 1)
        self.assertEqual(len(response.data['questions'][0]['answers']), 1)
    
    def test_update_quiz(self):
        """Test updating quiz title and description"""
        quiz = Quiz.objects.create(
            user=self.user,
            title='Old Title',
            youtube_url='https://youtube.com/watch?v=test'
        )
        
        url = reverse('quiz-detail', kwargs={'pk': quiz.id})
        data = {'title': 'New Title'}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'New Title')
    
    def test_delete_quiz(self):
        """Test deleting a quiz"""
        quiz = Quiz.objects.create(
            user=self.user,
            title='To Delete',
            youtube_url='https://youtube.com/watch?v=test'
        )
        
        url = reverse('quiz-detail', kwargs={'pk': quiz.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Quiz.objects.filter(id=quiz.id).exists())