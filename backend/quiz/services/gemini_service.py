import json
from typing import List, Dict
from google import genai
from django.conf import settings

QUIZ_PROMPT_TEMPLATE = """Based on the following transcript, generate a quiz in valid JSON format.

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


class GeminiQuizGenerator:
    """Service for generating quiz questions using Google Gemini AI."""

    def __init__(self):
        """Initialize the Gemini client with the API key from settings."""
        self.api_key = settings.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not configured in settings")
        self.client = genai.Client(api_key=self.api_key)

    def generate_quiz(self, transcription: str) -> Dict:
        """Generate quiz title, description, and questions from a transcription."""
        prompt = self._build_prompt(transcription)
        try:
            response = self.client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=prompt,
            )
            return self._parse_and_validate(response.text)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse Gemini response as JSON: {str(e)}")
        except Exception as e:
            raise Exception(f"Error generating quiz: {str(e)}")

    def _build_prompt(self, transcription: str) -> str:
        """Format the prompt template with the given transcription."""
        return QUIZ_PROMPT_TEMPLATE.format(transcription=transcription)

    def _parse_and_validate(self, response_text: str) -> Dict:
        """Parse the Gemini JSON response and validate the question list."""
        data = self._parse_response(response_text)
        self._validate_questions(data['questions'])
        return data

    def _parse_response(self, response_text: str) -> Dict:
        """Strip markdown fences and parse JSON from the Gemini response."""
        text = response_text.strip()
        if text.startswith('```json'):
            text = text[7:]
        elif text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
        return json.loads(text.strip())

    def _validate_questions(self, questions: List[Dict]):
        """Raise ValueError if the list does not contain exactly 10 valid questions."""
        if not isinstance(questions, list) or len(questions) != 10:
            count = len(questions) if isinstance(questions, list) else 'non-list'
            raise ValueError(f"Expected 10 questions, got {count}")
        for i, q in enumerate(questions):
            self._validate_single_question(q, i)

    def _validate_single_question(self, q: Dict, i: int):
        """Raise ValueError if a question is missing required fields or has wrong options."""
        if 'question_title' not in q:
            raise ValueError(f"Question {i} missing 'question_title'")
        if not isinstance(q.get('question_options'), list) or len(q['question_options']) != 4:
            raise ValueError(f"Question {i} must have exactly 4 options")
        if 'answer' not in q or q['answer'] not in q['question_options']:
            raise ValueError(f"Question {i} answer must be one of the 4 options")
