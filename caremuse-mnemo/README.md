# 🧠 CareMuse + Mnemo

A comprehensive, memory-aware digital companion that integrates personal journaling, intelligent AI conversation, brain games, health tracking, and clinical interactions in a respectful and privacy-preserving way — tailored for individuals with memory impairments.

## ✨ Features

### 💭 Memory Journal
- **Daily Journaling**: Capture thoughts, experiences, and daily moments
- **Smart Categorization**: Organize memories by type (diary, experience, gratitude, etc.)
- **Mood Tracking**: Record emotional states with each entry
- **Vector Search**: Find relevant memories using AI-powered similarity search
- **Tag System**: Organize memories with custom tags

### 👥 Persona-Based Conversations
Chat with different AI personas, each with unique personalities:
- **🤖 AI Companion**: Caring digital friend for everyday support
- **👨 Son**: Loving and supportive family member
- **👩 Daughter**: Warm and nurturing family connection
- **🩺 Doctor**: Professional medical guidance and health discussions
- **👩‍⚕️ Nurse**: Practical health advice and daily care support
- **🧠 Therapist**: Emotional support and mental health guidance

### 🏥 Medical Center
- **Document Upload**: OCR processing of medical reports, prescriptions, and lab results
- **AI Summarization**: Automatic summarization of medical documents
- **Secure Storage**: Medical information stored separately from personal memories
- **Healthcare Chat**: Discuss medical documents with doctor/nurse personas
- **Health Statistics**: Track and visualize health metrics over time

### 🧠 Brain Games & Exercises
- **Memory Match**: Card matching game to exercise visual memory
- **Number Sequence**: Remember and repeat number sequences
- **Quick Math**: Fast-paced arithmetic challenges
- **Progress Tracking**: Monitor cognitive performance over time
- **Achievements**: Unlock rewards for consistent play

### ⏰ Smart Reminders
- **Medication Reminders**: Never miss important medications
- **Appointment Alerts**: Keep track of medical appointments
- **Daily Tasks**: Remember important daily activities
- **Custom Scheduling**: Set personalized reminder times

### 📊 Health Tracking
- **Vital Signs**: Track blood pressure, heart rate, temperature
- **Lifestyle Metrics**: Monitor water intake, exercise, sleep
- **Mood Monitoring**: Daily emotional wellbeing check-ins
- **Progress Visualization**: Charts and graphs of health trends

### 📜 Chat History & Analytics
- **Conversation Search**: Find past conversations by keyword
- **Usage Statistics**: Understand interaction patterns
- **Export Functionality**: Download conversation history
- **Privacy Controls**: Manage data retention and deletion

## 🏗️ Architecture

### Backend (FastAPI)
```
backend/
├── app.py                 # Main API server
├── memory_manager.py      # Memory storage and retrieval
├── embeddings.py          # Text embedding generation
├── llm_interface.py       # Ollama LLM integration
├── medical_uploads.py     # Document processing and OCR
├── chat_logger.py         # Conversation history management
├── personas/              # AI persona configurations
│   ├── companion.yaml
│   ├── son.yaml
│   ├── daughter.yaml
│   ├── doctor.yaml
│   ├── nurse.yaml
│   └── therapist.yaml
├── db.sqlite             # SQLite database
├── faiss_personal.index  # Personal memory vector index
└── faiss_medical.index   # Medical memory vector index
```

### Frontend (Streamlit)
```
frontend/
├── pages/                # Main application pages
│   ├── home.py          # Dashboard and navigation
│   ├── memory.py        # Memory journal interface
│   ├── medical.py       # Medical document management
│   └── chat_history.py  # Conversation history viewer
├── modules/             # Feature modules
│   ├── companion.py     # Persona chat interface
│   ├── games.py         # Brain games and exercises
│   ├── reminders.py     # Reminder management
│   └── health.py        # Health tracking interface
└── utils/               # Utility functions
    ├── api_client.py    # Backend API communication
    ├── state.py         # Session state management
    └── styles.py        # Custom CSS styling
```

## 🔒 Privacy & Security

### Memory Scope Separation
- **Personal Memories**: Accessible to family personas (companion, son, daughter)
- **Medical Memories**: Only accessible to healthcare personas (doctor, nurse, therapist)
- **Chat Logs**: Scoped per persona for privacy

### Data Protection
- Local SQLite database for structured data
- Local FAISS indices for vector search
- No cloud dependencies for sensitive data
- Optional data export for backup

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Ollama (for LLM functionality)
- Tesseract OCR (for document processing)

### Backend Setup
```bash
cd caremuse-mnemo/backend

# Install dependencies
pip install -r requirements.txt

# Install Ollama and pull a model
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull mistral

# Install Tesseract OCR
# Ubuntu/Debian:
sudo apt-get install tesseract-ocr
# macOS:
brew install tesseract
# Windows: Download from GitHub releases

# Start the backend server
python app.py
```

### Frontend Setup
```bash
cd caremuse-mnemo/frontend

# Install dependencies
pip install -r requirements.txt

# Start the Streamlit app
streamlit run pages/home.py
```

### Docker Setup (Optional)
```bash
# Build and run with Docker Compose
docker-compose up --build
```

## 🎯 Usage Guide

### Getting Started
1. **Launch the Application**: Open your browser to `http://localhost:8501`
2. **User Onboarding**: Enter your name to personalize the experience
3. **Explore Features**: Use the sidebar navigation to access different modules

### Daily Workflow
1. **Morning Check-in**: Log your mood and any overnight thoughts
2. **Memory Journaling**: Record daily experiences and meaningful moments
3. **Health Tracking**: Log vital signs and wellness metrics
4. **Persona Conversations**: Chat with family members or healthcare providers
5. **Brain Games**: Exercise your mind with cognitive challenges
6. **Evening Reflection**: Review the day and set reminders for tomorrow

### Medical Document Management
1. **Upload Documents**: Use the Medical Center to upload reports
2. **AI Processing**: Documents are automatically processed with OCR and summarization
3. **Healthcare Discussions**: Chat with doctor/nurse personas about your documents
4. **Privacy Assurance**: Medical data is kept separate from personal memories

## 🛠️ Technical Details

### AI & Machine Learning
- **Embeddings**: Sentence Transformers for semantic search
- **Vector Search**: FAISS for efficient similarity matching
- **LLM Integration**: Ollama for local language model inference
- **OCR Processing**: Tesseract for document text extraction

### Database Schema
- **Memories Table**: Stores all user memories with metadata
- **Chat Conversations**: Logs all persona interactions
- **Vector Indices**: Separate FAISS indices for personal and medical memories

### API Endpoints
- `POST /store_memory` - Store new memory entries
- `GET /search_memories` - Vector similarity search
- `POST /chat` - Persona conversation
- `POST /upload_medical` - Medical document processing
- `GET /get_chat_history` - Retrieve conversation history

## 🧪 Development

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests (if implemented)
cd frontend
python -m pytest
```

### Code Quality
```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## 📈 Roadmap

### Planned Features
- [ ] Voice interaction capabilities
- [ ] Mobile app companion
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Integration with wearable devices
- [ ] Caregiver dashboard
- [ ] Backup and sync functionality

### Technical Improvements
- [ ] Enhanced security measures
- [ ] Performance optimizations
- [ ] Advanced AI models
- [ ] Real-time notifications
- [ ] Offline functionality

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines for details on:
- Code style and standards
- Pull request process
- Issue reporting
- Feature requests

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Streamlit** - For the amazing web app framework
- **FastAPI** - For the robust backend API framework
- **Ollama** - For local LLM inference capabilities
- **Sentence Transformers** - For semantic search functionality
- **FAISS** - For efficient vector similarity search

## 📞 Support

For questions, issues, or feature requests:
- 📧 Email: support@caremuse-mnemo.com
- 🐛 Issues: GitHub Issues
- 📖 Documentation: GitHub Wiki
- 💬 Discussions: GitHub Discussions

---

**CareMuse + Mnemo** - Empowering individuals with memory challenges through compassionate AI technology. 🧠💙