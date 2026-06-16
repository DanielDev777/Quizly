import os
import tempfile
from typing import Dict, Optional
import yt_dlp
import whisper

class YouTubeTranscriptionService:
    """Service for downloading YouTube videos and transcribing them with Whisper AI."""

    def __init__(self, whisper_model: str = 'base'):
        """Initialize service with Whisper model."""
        self.whisper_model_name = whisper_model
        self._whisper_model = None

    def _load_whisper_model(self):
        """Lazy load Whisper model (only when needed, ~75MB download first time)"""
        if self._whisper_model is None:
            print(f"Loading Whisper model: {self.whisper_model_name}")
            self._whisper_model = whisper.load_model(self.whisper_model_name)
        return self._whisper_model
    
    def get_video_info(self, youtube_url: str) -> Dict:
        """
        Extract metadata from YouTube video without downloading.
        Returns title.
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                return {
                    'title': info.get('title'),
                }
        except Exception as e:
            raise Exception(f"Error extracting video info: {str(e)}")
    
    def download_audio(self, youtube_url: str, output_path: Optional[str] = None) -> str:
        """
        Download audio from YouTube video as MP3.
        Returns the path to the downloaded audio file.
        """
        if output_path is None:
            temp_dir = tempfile.mkdtemp()
            output_path = os.path.join(temp_dir, 'audio')
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': output_path,
            'quiet': True,
        }
        
        try:
            print(f"Downloading audio from {youtube_url}...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])
            return f"{output_path}.mp3"
        except Exception as e:
            raise Exception(f"Error downloading audio: {str(e)}")
    
    def transcribe_audio(self, audio_path: str) -> Dict:
        """Transcribe audio file using Whisper AI."""
        try:
            print("Transcribing audio with Whisper...")
            model = self._load_whisper_model()
            result = model.transcribe(audio_path)
            
            return {
                'text': result['text'].strip(),
                'language': result.get('language', 'unknown'),
            }
        except Exception as e:
            raise Exception(f"Error transcribing audio: {str(e)}")
    
    def process_youtube_video(self, youtube_url: str) -> Dict:
        """Complete pipeline: get info, download audio, transcribe, cleanup."""
        audio_path = None
        
        try:
            video_info = self.get_video_info(youtube_url)
            print(f"Processing video: {video_info['title']}")
            
            audio_path = self.download_audio(youtube_url)
            
            transcription = self.transcribe_audio(audio_path)
            
            return {
                'transcription': transcription['text'],
                'language': transcription['language'],
            }
        
        finally:
            if audio_path and os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                    print(f"Cleaned up temporary file: {audio_path}")
                except:
                    pass