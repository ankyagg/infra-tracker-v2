# CivicGuard 🛡️

An AI-powered civic infrastructure monitoring platform that uses computer vision to analyze road damage, fallen poles, and civic hazards instantly. Help us build safer cities.

## 🎯 Problem Statement

Infrastructure damage assessment is time-consuming and often requires manual inspection by experts. This delays response times during emergencies. CivicGuard enables citizen reporting with instant AI-powered damage severity analysis and streamlined admin management.

## ✨ Features

### 1. **AI-Powered Damage Analysis**
- Upload/capture images of infrastructure damage
- Google Gemini AI (gemini-2.5-flash) analyzes images and provides:
  - Risk Level (1-5 scale)
  - Safety Risk Assessment  
  - Urgency Classification (low/medium/high/critical)
  - Damage Type Detection
  - Recommended Actions

### 2. **User Authentication System**
- Secure signup/login with password hashing (SHA-256 + salt)
- Role-based access control (Admin/User)
- Admin whitelist for authorized personnel
- Session token management
- Login tracking with timestamps

### 3. **Admin Dashboard**
- Real-time report monitoring
- Filter by: All Reports, Critical, Resolved
- Statistics overview (Total, Critical, Resolved)
- Detailed report modal with AI analysis
- One-click status updates
- Google Maps integration for locations
- Fully responsive for mobile devices

### 4. **Mobile-First Design**
- Responsive UI across all screen sizes
- Camera-only capture on mobile (no gallery)
- Touch-friendly hamburger menu
- Optimized image compression
- Mobile-friendly modals and cards

### 5. **Real-Time Location Tracking**
- GPS coordinates capture
- Automatic location tagging
- Google Maps links for navigation

### 6. **Cloud Storage & Database**
- Appwrite for image storage
- Firebase Firestore for data persistence
- Secure credential management
- Image proxy for admin access

## 🛠️ Tech Stack

### Frontend
- **HTML5/CSS3/JavaScript** - Responsive UI
- **Font Awesome** - Icons
- **Geolocation API** - GPS integration
- **Canvas API** - Image compression

### Backend
- **Python Flask** - REST API server
- **Google Gemini AI** - Image analysis (gemini-2.5-flash model)
- **Appwrite Cloud** - Image storage
- **Firebase Admin SDK** - Database
- **Pillow (PIL)** - Image processing

### Security
- SHA-256 password hashing with salt
- Session token authentication
- Role-based access control
- Environment variables for secrets
- Secret file handling on Render

### Deployment
- **Render.com** - Backend hosting
- **GitHub** - Version control

## 📋 Project Structure

```
civicguard/
├── index.html              # Landing page
├── app.html                # Report submission page
├── login.html              # Authentication page
├── admin.html              # Admin dashboard
├── script.js               # Frontend logic
├── style.css               # Global styling
├── backend/
│   ├── app.py              # Flask API server
│   ├── admin_whitelist.json # Admin email whitelist
│   └── serviceAccountKey.json # Firebase credentials
├── requirements.txt        # Python dependencies
├── Procfile                # Render deployment config
├── render.yaml             # Render service config
└── README.md               # Documentation
```

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Google Gemini API Key
- Firebase project with service account
- Appwrite project and API Key

### Environment Variables

Create a `.env` file in the backend folder:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1
APPWRITE_PROJECT_ID=your_project_id
APPWRITE_API_KEY=your_api_key
APPWRITE_BUCKET_ID=your_bucket_id
```

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/ankyagg/infra-tracker-v2.git
   cd infra-tracker-v2
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Add Firebase credentials**
   - Download `serviceAccountKey.json` from Firebase Console
   - Place in `backend/` folder

4. **Configure admin whitelist**
   - Edit `backend/admin_whitelist.json`
   - Add authorized admin emails

5. **Run the app**
   ```bash
   cd backend
   python app.py
   ```
   Visit `http://localhost:5000`

### Admin Whitelist Configuration

Edit `backend/admin_whitelist.json`:
```json
{
  "admin_emails": [
    "admin1@example.com",
    "admin2@example.com"
  ],
  "description": "Only emails listed here will get 'admin' role"
}
```

## 📊 API Endpoints

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/signup` | POST | Create new account |
| `/auth/login` | POST | Login and get token |
| `/auth/verify` | POST | Verify session token |
| `/auth/logout` | POST | Invalidate token |

### Reports

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/submit-report` | POST | Submit damage report |
| `/get-reports` | GET | Get all reports |
| `/update-report-status` | POST | Update report status |

### Utilities

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/image/<file_id>` | GET | Proxy for Appwrite images |
| `/submit-feedback` | POST | Submit feedback |

## 🤖 AI Analysis Output

```json
{
  "risk_level": 4,
  "safety_risk": 3,
  "urgency": "high",
  "damage_type": "Deep pothole with exposed rebar",
  "recommended_actions": [
    "Immediate area cordoning required",
    "Contact road maintenance department",
    "Install warning signs"
  ],
  "assessment": "Severe road damage requiring urgent attention..."
}
```

## 🔐 Security Features

- **Password Hashing**: SHA-256 with random 16-byte salt
- **Session Tokens**: Secure random tokens (32 bytes)
- **Role-Based Access**: Admin whitelist controls dashboard access
- **Environment Variables**: All secrets stored securely
- **HTTPS**: Encrypted connections on Render

## 📱 Mobile Features

- Camera-only capture (prevents gallery uploads)
- Responsive navbar with login/logout
- Hamburger menu for admin sidebar
- Touch-optimized buttons and cards
- Full-screen modals on small screens

## 📈 Database Schema

### Users Collection
```json
{
  "email": "user@example.com",
  "password": "salt:hash",
  "name": "John Doe",
  "role": "admin|user",
  "created_at": "2026-01-17T10:30:00+05:30",
  "last_logged_in": "2026-01-17T14:45:00+05:30"
}
```

### Reports Collection
```json
{
  "id": "unique_report_id",
  "category": "Road Damage",
  "description": "Large pothole",
  "location": "19.0760, 72.8777",
  "image": "appwrite_file_url",
  "status": "Reported|In Progress|Resolved",
  "timestamp": "2026-01-17T12:00:00+05:30",
  "risk_assessment": {
    "risk_level": 4,
    "safety_risk": 3,
    "urgency": "high",
    "damage_type": "...",
    "recommended_actions": []
  }
}
```

## 🎓 Learning Outcomes

This project demonstrates:
- Full-stack web development
- AI/ML integration with Google Gemini
- Authentication & authorization systems
- Cloud deployment and scaling
- Image processing and optimization
- REST API design
- Mobile-first responsive design
- Security best practices

## 👥 Contributors

- **Aniket Walanj** 
- **Kuhu Vilecha** 
- **Dishita Vaswani** 

## 📝 License

MIT License - Feel free to use and modify

## 🌐 Live Demo

- **Application**: https://infra-tracker.onrender.com

---

**Built with ❤️ for Safer Cities**
