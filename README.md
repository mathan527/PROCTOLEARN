# ProctoLearn - AI-Powered Online Proctoring System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.4-green.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-blue.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![TensorFlow.js](https://img.shields.io/badge/TensorFlow.js-4.15-orange.svg)](https://www.tensorflow.org/js)

An advanced online examination platform with real-time AI-powered proctoring, automated question generation, and comprehensive monitoring capabilities.

## 🚀 Features

### Core Functionality
- **Multi-Role Authentication**: Separate dashboards for Students, Teachers, and Administrators
- **Test Creation & Management**: Intuitive test builder with multiple question types
- **Real-time Proctoring**: Live monitoring with AI-powered violation detection
- **WebRTC Streaming**: Real-time video and screen sharing for proctored exams
- **Automated Grading**: Instant scoring and detailed analytics

### AI-Powered Features
- **Smart Question Generation**: Generate questions from PDF documents using Groq AI
- **Face Detection**: Real-time face recognition and tracking
- **Behavioral Analysis**: Monitor eye movement, head pose, and screen focus
- **Object Detection**: Identify unauthorized objects in the testing environment
- **Audio Monitoring**: Real-time audio level analysis

### Proctoring Capabilities
- **Multi-Stream Monitoring**: Simultaneous camera and screen recording
- **Violation Detection**: Automatic detection of tab switching, fullscreen exit, and suspicious behavior
- **Waiting Room System**: Teacher-controlled test admission
- **Real-time Alerts**: Instant notifications for proctoring violations
- **Session Recording**: Complete test session archival

### Security Features
- **Encrypted PDFs**: Support for password-protected documents
- **Browser Lockdown**: Prevent unauthorized browser actions
- **Session Validation**: Secure test session management
- **Violation Logging**: Comprehensive audit trails

## 🏗️ Architecture

### Frontend (Vue.js 3)
- **Framework**: Vue 3 with Composition API
- **UI Library**: Tailwind CSS for responsive design
- **State Management**: Pinia for centralized state
- **Real-time Communication**: Socket.IO for live updates
- **WebRTC**: Peer-to-peer video streaming

### Backend (FastAPI)
- **Framework**: FastAPI with async SQLAlchemy
- **Database**: PostgreSQL with connection pooling
- **Authentication**: JWT-based secure authentication
- **File Processing**: OCR and PDF text extraction
- **AI Integration**: Groq API for question generation

### AI/ML Components
- **Face Detection**: MediaPipe Face Detection
- **Face Landmarks**: MediaPipe Face Mesh for head pose estimation
- **Object Detection**: COCO-SSD for environment monitoring
- **Audio Analysis**: Real-time audio level monitoring

## 📋 Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.9+
- **PostgreSQL** 15+
- **Tesseract OCR** (for PDF processing)
  - **Windows**: Download from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)
  - **Linux**: `sudo apt-get install tesseract-ocr`
  - **macOS**: `brew install tesseract`
- **Git** for version control

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/magi8101/proctolearn.git
cd proctolearn
```

### 2. Environment Setup

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
# Set database URL, JWT secrets, Groq API key, etc.
```

#### Frontend Setup
```bash
cd ../src

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
```

### 3. Database Setup
```bash
# Create PostgreSQL database
createdb proctolearn

# Run migrations
cd backend
alembic upgrade head
```

### 4. Start Services

```

#### Manual startup

**Terminal 1 - Backend:**
```bash
cd backend
python run.py
```

**Terminal 2 - Frontend:**
```bash
cd src
npm run dev
```

### 5. Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://user:password@localhost/proctolearn

# JWT
JWT_SECRET_KEY=your-super-secret-jwt-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Services
GROQ_API_KEY=your-groq-api-key

# OCR Configuration
TESSERACT_CMD=YOURE_OCR_PATH

# File Upload
UPLOAD_DIR=uploads/
MAX_FILE_SIZE=10485760

```

#### Frontend (.env)
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_SOCKET_URL=http://localhost:8000
VITE_GROQ_API_KEY=your-groq-api-key
```

## 📖 Usage Guide

### For Teachers
1. **Create Tests**: Use the intuitive test builder with AI question generation
2. **Upload Materials**: Support for PDF documents with automatic text extraction
3. **Monitor Sessions**: Real-time proctoring dashboard with live student feeds
4. **Review Violations**: Detailed violation logs and session recordings

### For Students
1. **Join Tests**: Enter test codes to access examinations
2. **Camera Setup**: Grant permissions for video monitoring
3. **Take Exams**: Secure testing environment with real-time monitoring
4. **Submit Results**: Automatic submission with instant feedback

### For Administrators
1. **User Management**: Create and manage teacher/student accounts
2. **System Monitoring**: View system health and usage statistics
3. **Audit Logs**: Comprehensive system activity tracking

## 🔒 Security Considerations

- **HTTPS Required**: All production deployments must use HTTPS
- **Secure Secrets**: Never commit API keys or secrets to version control
- **Database Encryption**: Sensitive data should be encrypted at rest
- **Regular Updates**: Keep dependencies updated for security patches
- **Access Controls**: Implement proper role-based access controls

## 🧪 Testing

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd src
npm test
```



## 🚀 Deployment

### Production Deployment
1. **Environment Setup**: Configure production database and secrets
2. **SSL Certificates**: Enable HTTPS with valid certificates
3. **Reverse Proxy**: Use Nginx or Apache as reverse proxy
4. **Process Manager**: Use PM2 or systemd for process management
5. **Monitoring**: Set up logging and monitoring solutions


## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow Vue.js and FastAPI best practices
- Write comprehensive tests for new features
- Update documentation for API changes
- Ensure cross-browser compatibility

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Vue.js** - Progressive JavaScript framework
- **FastAPI** - Modern Python web framework
- **MediaPipe** - Cross-platform ML solutions
- **TensorFlow.js** - Machine learning in JavaScript
- **Groq** - Fast AI inference platform

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review existing issues for similar problems

## 🔄 Version History

### v1.0.0 (Current)
- Complete AI-powered proctoring system
- Real-time video monitoring
- Automated question generation
- Multi-role user management
- Comprehensive violation detection

---

**Built with ❤️ for secure and fair online examinations**