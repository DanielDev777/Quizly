# 🎯 Quizly - YouTube Quiz Generator Backend

Transform YouTube videos into interactive quizzes using AI! This project guides you through building a Django REST API backend that automatically transcribes YouTube videos using Whisper and generates quiz questions using Google Gemini AI.

## 🌟 What You'll Build

- **🎥 YouTube Integration**: Download and process any YouTube video
- **🎤 AI Transcription**: Automatic speech-to-text using OpenAI Whisper
- **🤖 Smart Quiz Generation**: Generate multiple-choice questions with Google Gemini AI
- **🔐 JWT Authentication**: Secure user authentication with access & refresh tokens
- **📚 Quiz Management**: Full CRUD operations for quizzes
- **🎨 RESTful API**: Clean, well-documented REST API endpoints
- **🛡️ User-based Isolation**: Each user can only access their own quizzes

## 📚 Documentation

This project includes comprehensive step-by-step guides:

- **[QUICKSTART.md](QUICKSTART.md)** - Get up and running in 15 minutes
- **[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)** - Complete tutorial to code along with (recommended!)
- **[API_REFERENCE.md](API_REFERENCE.md)** - API endpoint documentation

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- FFmpeg (for audio processing)
- Google Gemini API key ([get one here](https://aistudio.google.com/app/apikey))

### Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.template .env
# Edit .env and add your SECRET_KEY and GEMINI_API_KEY

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start server
python manage.py runserver
```

Visit http://localhost:8000/admin to access the admin panel.

## 🔌 API Endpoints

### Authentication
```
POST   /api/register/          Register new user
POST   /api/login/             Login user
POST   /api/logout/            Logout user
POST   /api/token/refresh/     Refresh access token
```

### Quiz Management
```
POST   /api/quizzes/           Create quiz from YouTube URL
GET    /api/quizzes/           List all user's quizzes
GET    /api/quizzes/{id}/      Get quiz details with questions
PATCH  /api/quizzes/{id}/      Update quiz metadata
DELETE /api/quizzes/{id}/      Delete quiz
```

## 💡 Example Usage

```bash
# Register a user
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"user","password":"Pass123!","password2":"Pass123!"}'

# Create a quiz from YouTube video
curl -X POST http://localhost:8000/api/quizzes/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"youtube_url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ","title":"My Quiz"}'
```

## 🏗️ Project Structure

```
backend/
├── manage.py
├── requirements.txt
├── .env                      # Your configuration (create this)
├── core/                     # Django project settings
│   ├── settings.py
│   └── urls.py
├── auth_app/                 # Authentication
│   ├── models.py            # Custom User model
│   ├── views.py             # Auth endpoints
│   ├── serializers.py
│   └── urls.py
└── quiz/                     # Quiz management
    ├── models.py            # Quiz, Question, Answer models
    ├── views.py             # Quiz CRUD endpoints
    ├── serializers.py
    ├── urls.py
    └── services/            # Business logic (you'll create this)
        ├── youtube_service.py
        └── gemini_service.py
```

## 📦 Technology Stack

- **Framework**: Django 6.0.3
- **API**: Django REST Framework 3.17.1
- **Authentication**: djangorestframework-simplejwt 5.5.1
- **Transcription**: OpenAI Whisper
- **YouTube**: yt-dlp
- **AI**: Google Gemini API
- **Database**: SQLite (development) / PostgreSQL (production)

## 📖 Learning Path

1. **Start here**: Read [QUICKSTART.md](QUICKSTART.md) to set up your environment
2. **Code along**: Follow [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) step-by-step
3. **Reference**: Use [API_REFERENCE.md](API_REFERENCE.md) for endpoint details
4. **Test**: Try creating quizzes with different YouTube videos
5. **Extend**: Add features like quiz sharing, user scores, or custom question editing

## ⚡ Performance Notes

### Quiz Creation Time
- **Short video (5 min)**: ~1-2 minutes
- **Medium video (15 min)**: ~3-5 minutes
- **Long video (30+ min)**: ~5-10 minutes

Processing includes downloading, transcription, and AI generation. For production, implement Celery for background processing (covered in the implementation guide).

### Whisper Model Options

| Model  | Speed | Accuracy | Use Case |
|--------|-------|----------|----------|
| tiny   | ⚡⚡⚡ | ⭐⭐     | Quick testing |
| base   | ⚡⚡⚡ | ⭐⭐⭐   | Development (default) |
| small  | ⚡⚡  | ⭐⭐⭐⭐ | Production |
| medium | ⚡    | ⭐⭐⭐⭐⭐ | High accuracy |
| large  | ⚡    | ⭐⭐⭐⭐⭐ | Best quality |

## 🛠️ Development Tips

- **Start with short videos**: Test with 1-5 minute videos while developing
- **Monitor console output**: Watch the logs to see processing progress
- **Use the admin panel**: Great for inspecting quiz data at http://localhost:8000/admin
- **Check API responses**: Use cURL or Postman to test endpoints
- **Read the guide**: The [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) has detailed explanations

## 🔒 Security Features

- ✅ JWT-based authentication
- ✅ Password hashing with Django's built-in system
- ✅ User-based resource isolation (users can only see their own quizzes)
- ✅ Input validation with DRF serializers
- ✅ CORS configuration for frontend integration
- ✅ Environment variable protection
- ✅ SQL injection protection (Django ORM)

## 🚀 Production Deployment

The implementation guide includes a section on production deployment covering:
- PostgreSQL database setup
- Celery for background tasks
- Redis for caching
- Gunicorn + Nginx configuration
- Security hardening
- Error monitoring with Sentry

## 🆘 Common Issues

**FFmpeg not found**: Install FFmpeg and add to PATH  
**Gemini API key error**: Add GEMINI_API_KEY to `.env`  
**Slow transcription**: Use smaller Whisper model or implement Celery  
**Invalid YouTube URL**: Ensure video is public and accessible

See [QUICKSTART.md](QUICKSTART.md) for more troubleshooting tips.

## 📝 License

This project is for educational purposes. Check individual library licenses:
- Django: BSD License
- Whisper: MIT License
- Google Gemini: Google APIs Terms of Service

---

**Ready to build? Start with [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)!** 🚀
