# Smart Air Pollution Monitoring System

Real-time air quality monitoring system using Django, React, and OpenWeather API.

## 🌟 Features
- Real-time AQI data for cities worldwide
- Historical trends and analytics
- 7-day ML-powered forecasts
- Health advisories
- Beautiful responsive UI

## 🛠️ Tech Stack
- **Backend:** Django REST Framework
- **Frontend:** React + Tailwind CSS
- **Database:** SQLite
- **API:** OpenWeather Air Pollution API
- **ML:** Scikit-learn (Random Forest)

## 📋 Prerequisites
- Python 3.8+
- Node.js 16+
- OpenWeather API Key

## 🚀 Setup Instructions

### Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Environment Variables
Create `backend/.env`:
```
OPENWEATHER_API_KEY=your_api_key_here
```

## 👥 Team
- Abdullah Amjad (2024-DS-37)
- Syed Muhammad Fahad (2024-DS-46)
- Muhammad Danish (2024-DS-54)

Institute of Data Science, UET Lahore

## 📄 License
Academic Project - UET Lahore



