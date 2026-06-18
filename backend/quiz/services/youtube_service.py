import os
import tempfile
from typing import Dict, Optional
import yt_dlp
import whisper


class YouTubeTranscriptionService:
    """Service for downloading YouTube audio and transcribing it with Whisper AI."""

    def __init__(self, whisper_model: str = 'base'):
        """Initialize service with the name of the Whisper model to use."""
        self.whisper_model_name = whisper_model
        self._whisper_model = None

    def _load_whisper_model(self):
        """Lazy-load the Whisper model (downloads ~75 MB on first use)."""
        if self._whisper_model is None:
            self._whisper_model = whisper.load_model(self.whisper_model_name)
        return self._whisper_model

    def _get_ydl_options(self, output_path: str) -> Dict:
        """Build yt-dlp options for extracting audio as MP3."""
        return {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': output_path,
            'quiet': True,
        }

    def download_audio(self, youtube_url: str, output_path: Optional[str] = None) -> str:
        """Download audio from a YouTube video as MP3, return path to the file."""
        if output_path is None:
            output_path = os.path.join(tempfile.mkdtemp(), 'audio')
        try:
            with yt_dlp.YoutubeDL(self._get_ydl_options(output_path)) as ydl:
                ydl.download([youtube_url])
            return f"{output_path}.mp3"
        except Exception as e:
            raise Exception(f"Error downloading audio: {str(e)}")

    def transcribe_audio(self, audio_path: str) -> Dict:
        """Transcribe an audio file with Whisper AI, return text and language."""
        try:
            result = self._load_whisper_model().transcribe(audio_path)
            return {
                'text': result['text'].strip(),
                'language': result.get('language', 'unknown'),
            }
        except Exception as e:
            raise Exception(f"Error transcribing audio: {str(e)}")

    def _cleanup_file(self, path: Optional[str]):
        """Delete a temporary file if it exists, silently ignoring any error."""
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass

    def process_youtube_video(self, youtube_url: str) -> Dict:
        """Download audio, transcribe with Whisper, clean up, and return result."""
        audio_path = None
        try:
            audio_path = self.download_audio(youtube_url)
            transcription = self.transcribe_audio(audio_path)
            return {
                'transcription': transcription['text'],
                'language': transcription['language'],
            }
        finally:
            self._cleanup_file(audio_path)
