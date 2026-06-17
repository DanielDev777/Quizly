import json
from typing import List, Dict
from google import genai
from django.conf import settings

class GeminiQuizGenerator:
    """Service for generating quiz questions using Google Gemini AI."""

    def __init__(self):
        """Initialize Gemini client with API key from settings"""
        self.api_key = settings.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not configured in settings")
        
        self.client = genai.Client(api_key=self.api_key)

    def generate_quiz(self, transcription: str) -> List[Dict]:
        """Generate quiz questions from video transcription."""
        prompt = self._build_prompt(transcription)

        try:
            response = self.client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=prompt
            )

            questions = self._parse_response(response.text)
            self._validate_questions(questions)
            return questions

        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse Gemini response as JSON: {str(e)}")
        except Exception as e:
            raise Exception(f"Error generating quiz: {str(e)}")

        
    def _build_prompt(self, transcription: str) -> str:
        """Build the AI prompt with specific formatting requirements"""
        return f"""Based on the following transcript, generate a quiz in valid JSON format.

        VIDEO TRANSCRIPTION:
        {transcription}

        The quiz must follow this exact structure:

        {{

        "title": "Create a concise quiz title based on the topic of the transcript.",

        "description": "Summarize the transcript in no more than 150 characters. Do not include any quiz questions or answers.",

        "questions": [

            {{

            "question_title": "The question goes here.",

            "question_options": ["Option A", "Option B", "Option C", "Option D"],

            "answer": "The correct answer from the above options"

            }},

            ...

            (exactly 10 questions)

        ]

        }}

        Requirements:

        - Each question must have exactly 4 distinct answer options.

        - Only one correct answer is allowed per question, and it must be present in 'question_options'.

        - The output must be valid JSON and parsable as-is (e.g., using Python's json.loads).

        - Do not include explanations, comments, or any text outside the JSON."""

    def _parse_response(self, response_text: str) -> List[Dict]:
        text = response_text.strip()
        if text.startswith('```json'):
            text = text[7:]
        elif text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
        data = json.loads(text.strip())
        return data['questions']

    def _validate_questions(self, questions: List[Dict]):
        if not isinstance(questions, list):
            raise ValueError("Response must be a list of questions")
        if len(questions) != 10:
            raise ValueError(f"Expected 10 questions, got {len(questions)}")
        for i, q in enumerate(questions):
            if 'question_title' not in q:
                raise ValueError(f"Question {i} missing 'question_title'")
            if 'question_options' not in q or not isinstance(q['question_options'], list):
                raise ValueError(f"Question {i} missing or invalid 'question_options'")
            if len(q['question_options']) != 4:
                raise ValueError(f"Question {i} must have exactly 4 options")
            if 'answer' not in q:
                raise ValueError(f"Question {i} missing 'answer'")
            if q['answer'] not in q['question_options']:
                raise ValueError(f"Question {i} answer must be one of the options")