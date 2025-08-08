# 🎓 SkillSwap - Exchange Skills, Grow Together

> **The ultimate platform for students to exchange skills and knowledge without spending money - just time!**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.41-red.svg)](https://sqlalchemy.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌟 What is SkillSwap?

SkillSwap is a revolutionary web platform designed specifically for university students to exchange skills and knowledge. Instead of paying money for tutoring, services, or learning new skills, students can trade their expertise with peers using their time as currency.

### 🎯 Key Features

- **🔐 Secure Authentication** - User registration and login system
- **📚 Skill Management** - Add, view, and manage your skills
- **🤝 Skill Swapping** - Create and respond to skill exchange requests
- **💬 Real-time Chat** - Built-in messaging system for skill discussions
- **📊 Dashboard** - Personalized dashboard showing relevant swaps
- **🎨 Modern UI** - Beautiful, responsive design with Bootstrap 5
- **📱 Mobile-Friendly** - Works seamlessly on all devices

## 🚀 Live Demo

**Coming Soon!** - SkillSwap will be deployed to Render.com

## 🛠️ Technology Stack

### Backend
- **Python 3.11+** - Core programming language
- **Flask 3.0.0** - Web framework
- **SQLAlchemy 2.0.41** - Database ORM
- **Flask-SocketIO** - Real-time communication
- **PostgreSQL** - Production database
- **SQLite** - Development database

### Frontend
- **Bootstrap 5** - CSS framework
- **JavaScript** - Interactive features
- **Socket.IO** - Real-time chat
- **HTML5/CSS3** - Modern web standards

### Development Tools
- **pytest** - Testing framework
- **Flask-Migrate** - Database migrations
- **Alembic** - Migration tool
- **Gunicorn** - Production server

## 📦 Installation

### Prerequisites
- Python 3.11 or higher
- pip (Python package installer)
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/skillswap.git
   cd skillswap
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Create a .env file
   cp .env.example .env
   
   # Edit .env with your configuration
   SECRET_KEY=your-secret-key-here
   DATABASE_URI=sqlite:///skillswap.db
   ```

5. **Initialize the database**
   ```bash
   flask db upgrade
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

7. **Open your browser**
   Navigate to `http://localhost:8000`

## 🎨 Features in Detail

### 🔐 Authentication System
- Secure user registration with email validation
- Password hashing and security
- Session management
- User profile management

### 📚 Skill Categories
SkillSwap includes 14 comprehensive categories:
- **Academic Tutoring** - Calculus, Chemistry, Essay Writing
- **Tech & Programming** - Python, Web Design, Machine Learning
- **Creative Skills** - Design, Photography, Video Editing
- **Languages & Culture** - Spanish, French, ASL
- **Health & Wellness** - Yoga, Mindfulness, Fitness
- **Career Prep** - Resume Reviews, Interview Practice
- **And 9 more categories!**

### 🤝 Skill Swapping Process
1. **Add Your Skills** - List what you can teach/offer
2. **Browse Swaps** - Find skills you want to learn
3. **Make Requests** - Propose skill exchanges
4. **Chat & Discuss** - Use real-time messaging
5. **Complete Swaps** - Exchange skills and grow together

### 💬 Real-time Communication
- Instant messaging between users
- Real-time notifications
- Chat history
- File sharing capabilities

## 🏗️ Project Structure

```
SkillSwap/
├── app/                          # Main application package
│   ├── __init__.py
│   ├── app.py                   # Application factory
│   ├── config.py                # Configuration settings
│   ├── forms/                   # WTForms definitions
│   │   ├── login.py
│   │   ├── signup.py
│   │   ├── add_skill.py
│   │   └── make_swap.py
│   ├── models/                  # Database models
│   │   ├── user.py
│   │   ├── skill.py
│   │   ├── swap.py
│   │   └── ...
│   ├── routes/                  # Flask routes
│   │   ├── auth_routes.py
│   │   ├── dashboard_routes.py
│   │   ├── skill_routes.py
│   │   └── ...
│   ├── sockets/                 # WebSocket handlers
│   ├── static/                  # Static files (CSS, JS, images)
│   └── templates/               # HTML templates
├── tests/                       # Test suite
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_auth_routes.py
│   └── ...
├── requirements.txt             # Python dependencies
├── run.py                      # Application entry point
├── config.py                   # Configuration
└── README.md                   # This file
```

## 🧪 Testing

SkillSwap includes a comprehensive test suite:

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_models.py

# Run tests with verbose output
pytest -v
```

### Test Coverage
- ✅ Database models and relationships
- ✅ Authentication and authorization
- ✅ Form validation
- ✅ Route functionality
- ✅ Integration tests
- ✅ Security tests

## 🚀 Deployment

### Deploy to Render (Recommended)

1. **Fork this repository**
2. **Connect to Render**
   - Go to [render.com](https://render.com)
   - Create a new Web Service
   - Connect your GitHub repository
3. **Configure environment variables**
   - `SECRET_KEY` - Your secret key
   - `DATABASE_URL` - PostgreSQL database URL
4. **Deploy!**

### Manual Deployment

```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn run:app
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Add tests** for new functionality
5. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
6. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 style guidelines
- Write comprehensive tests
- Update documentation
- Use meaningful commit messages

## 📊 Roadmap

### Phase 1 (Current)
- ✅ User authentication
- ✅ Skill management
- ✅ Basic swapping system
- ✅ Real-time chat
- ✅ Mobile-responsive design

### Phase 2 (Planned)
- 🔄 Advanced search and filtering
- 🔄 Skill verification system
- 🔄 Rating and review system
- 🔄 Push notifications
- 🔄 Mobile app

### Phase 3 (Future)
- 📅 AI-powered skill matching
- 📅 Video calling integration
- 📅 Skill certification
- 📅 Community features
- 📅 Analytics dashboard

## 🐛 Bug Reports

If you find a bug, please create an issue with:
- **Description** of the bug
- **Steps to reproduce**
- **Expected behavior**
- **Screenshots** (if applicable)
- **Environment** (OS, browser, etc.)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Flask Community** - For the amazing web framework
- **Bootstrap Team** - For the beautiful UI components
- **SQLAlchemy Team** - For the powerful ORM
- **All Contributors** - For making SkillSwap better

## 📞 Contact

- **Project Link**: [https://github.com/yourusername/skillswap](https://github.com/yourusername/skillswap)
- **Issues**: [https://github.com/yourusername/skillswap/issues](https://github.com/yourusername/skillswap/issues)

---

<div align="center">

**Made with ❤️ for students everywhere**

[![GitHub stars](https://img.shields.io/github/stars/yourusername/skillswap?style=social)](https://github.com/yourusername/skillswap)
[![GitHub forks](https://img.shields.io/github/forks/yourusername/skillswap?style=social)](https://github.com/yourusername/skillswap)
[![GitHub issues](https://img.shields.io/github/issues/yourusername/skillswap)](https://github.com/yourusername/skillswap/issues)

</div>