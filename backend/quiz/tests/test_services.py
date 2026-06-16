from django.test import TestCase
from unittest.mock import patch, MagicMock
from quiz.services.youtube_service import YouTubeTranscriptionService
from quiz.services.gemini_service import GeminiQuizGenerator

class YouTubeServiceTests(TestCase):
    """Test YouTube transcription service"""
    
    def setUp(self):
        self.service = YouTubeTranscriptionService(whisper_model='tiny')
    
    @patch('yt_dlp.YoutubeDL')
    def test_get_video_info(self, mock_ytdl):
        """Test extracting video metadata"""
        mock_instance = MagicMock()
        mock_instance.extract_info.return_value = {
            'title': 'Test Video',
            'description': 'Test description',
            'uploader': 'Test Channel'
        }
        mock_ytdl.return_value.__enter__.return_value = mock_instance
        
        result = self.service.get_video_info('https://youtube.com/watch?v=test')
        
        self.assertEqual(result['title'], 'Test Video')
    
    @patch('yt_dlp.YoutubeDL')
    def test_download_audio(self, mock_ytdl):
        """Test audio download from YouTube"""
        mock_instance = MagicMock()
        mock_instance.download.return_value = None
        mock_ytdl.return_value.__enter__.return_value = mock_instance
        
        result = self.service.download_audio('https://youtube.com/watch?v=test')
        
        self.assertTrue(result.endswith('.mp3'))
        mock_instance.download.assert_called_once()
    
    @patch('whisper.load_model')
    def test_transcribe_audio(self, mock_load_model):
        """Test audio transcription with Whisper"""
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {
            'text': 'This is a test transcription',
            'language': 'en',
            'segments': []
        }
        mock_load_model.return_value = mock_model
        
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            audio_path = f.name
        
        result = self.service.transcribe_audio(audio_path)
        
        self.assertEqual(result['text'], 'This is a test transcription')
        self.assertEqual(result['language'], 'en')

class GeminiServiceTests(TestCase):
    """Test Gemini quiz generation service"""
    
    @patch('google.genai.Client')
    def test_generate_quiz(self, mock_client):
        mock_response = MagicMock()
        mock_response.text = '''{
            "title": "Python Quiz",
            "description": "A quiz about Python",
            "questions": [
                {
                    "question_title": "What is Python?",
                    "question_options": ["A programming language", "A snake", "A food", "A game"],
                    "answer": "A programming language"
                }
            ]
        }'''

        mock_instance = MagicMock()
        mock_instance.models.generate_content.return_value = mock_response
        mock_client.return_value = mock_instance

        service = GeminiQuizGenerator()
        result = service.generate_quiz('Test transcription about Python')

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['question_title'], 'What is Python?')
        self.assertEqual(len(result[0]['question_options']), 4)

    def test_validate_questions_success(self):
        service = GeminiQuizGenerator()
        questions = [
            {
                "question_title": "Test?",
                "question_options": ["A", "B", "C", "D"],
                "answer": "A"
            }
        ]
        service._validate_questions(questions)

    def test_validate_questions_answer_not_in_options(self):
        service = GeminiQuizGenerator()
        questions = [
            {
                "question_title": "Test?",
                "question_options": ["A", "B", "C", "D"],
                "answer": "E"  # not in options
            }
        ]
        with self.assertRaises(ValueError):
            service._validate_questions(questions)