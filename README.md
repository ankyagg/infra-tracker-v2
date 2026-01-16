# Infrastructure Damage Tracker 🏗️

An AI-powered web application that analyzes infrastructure damage using computer vision and provides risk-based alerts to authorities. Built for rapid damage assessment and emergency response coordination.

## 🎯 Problem Statement

Infrastructure damage assessment is time-consuming and often requires manual inspection by experts. This delays response times during emergencies. Our solution enables citizen reporting with instant AI-powered damage severity analysis.

## ✨ Features

### 1. **AI-Powered Damage Analysis**
- Upload images of infrastructure damage
- Gemini AI analyzes the image and provides:
  - Risk Level (1-5 scale)
  - Safety Risk Assessment
  - Urgency Classification (low/medium/high/critical)
  - Detailed structural assessment

### 2. **Real-Time Location Tracking**
- Get live GPS coordinates
- Automatic location capture for damage reports
- Geolocation integration for incident mapping

### 3. **Image Compression & Optimization**
- Automatic image compression to reduce bandwidth
- Converts to JPEG format for faster processing
- Maintains quality while optimizing file size

### 4. **Report Management**
- Generate unique report IDs
- Categorize damage types (Road Damage, Building Cracks, Leaning Pole, etc.)
- Add detailed descriptions and location data

### 5. **Feedback System**
- Users can provide feedback on AI analysis accuracy
- Tracks assessment reliability
- Helps improve model performance over time

### 6. **Firebase Integration**
- Persistent data storage
- Real-time database updates
- Secure report archival

## 🛠️ Tech Stack

### Frontend
- **HTML/CSS/JavaScript** - Responsive UI
- **Geolocation API** - GPS integration
- **Canvas API** - Image compression

### Backend
- **Python Flask** - REST API server
- **Google Gemini AI** - Image analysis & risk assessment
- **Appwrite Storage** - Cloud storage for images
- **Firebase Admin SDK** - Database & authentication
- **Pillow** - Image processing

### Deployment
- **Render.com** - Cloud hosting
- **GitHub Pages** - Static site hosting
- **Google Cloud** - AI/ML services

## 📋 Project Structure

```
infra-tracker-v2/
├── index.html              # Main reporting interface
├── admin.html              # Admin dashboard
├── script.js               # Frontend logic
├── style.css               # Styling
├── backend/
│   └── app.py             # Flask API server
├── requirements.txt        # Python dependencies
├── Procfile               # Render deployment config
├── render.yaml            # Render service config
└── README.md              # Documentation
```

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Google Gemini API Key
- Firebase project with service account
- Appwrite project and API Key
- Modern web browser

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/ankyagg/infra-tracker-v2.git
   cd infra-tracker-v2
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Create .env file
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```

5. **Add Firebase credentials**
   - Download `serviceAccountKey.json` from Firebase Console
   - Place in `backend/` folder

6. **Run the app**
   ```bash
   python app.py
   ```
   Visit `http://localhost:5000`

### Deployment on Render

1. Push to GitHub: `git push origin main`
2. Connect your GitHub repo on Render.com
3. Add environment variables:
   - `GEMINI_API_KEY` - Your Gemini API key
4. Add secret file:
   - Upload `serviceAccountKey.json` as `serviceAccountKey`
5. Deploy!

## 📊 API Endpoints

### Submit Report
**POST** `/submit-report`
```json
{
  "category": "Road Damage",
  "description": "Large pothole on main street",
  "location": "40.7128, -74.0060",
  "image": "data:image/jpeg;base64,..."
}
```

Response:
```json
{
  "status": "success",
  "id": "report_id_123",
  "risk_assessment": {
    "risk_level": 3,
    "safety_risk": 2,
    "urgency": "medium",
    "assessment": "..."
  }
}
```

### Submit Feedback
**POST** `/submit-feedback`
```json
{
  "report_id": "report_id_123",
  "feedback_type": "accurate",
  "feedback_comment": "Assessment was accurate"
}
```

## 🤖 AI Analysis Criteria

### Risk Level (1-5)
- **1**: No damage or minimal cosmetic damage
- **2**: Minor damage, no immediate safety threat
- **3**: Moderate damage requiring attention within weeks
- **4**: Significant damage requiring urgent repair within days
- **5**: Critical damage requiring immediate closure

### Safety Risk (1-5)
- **1**: No public safety risk
- **2**: Minimal risk to pedestrians
- **3**: Moderate risk, hazard for vulnerable groups
- **4**: High risk, danger to all
- **5**: Extreme risk, severe injury/death possibility

## 📈 Impact & Use Cases

- **Emergency Response**: Rapid damage severity assessment
- **City Planning**: Track infrastructure health across regions
- **Insurance Claims**: Automated damage documentation
- **Civic Participation**: Enable citizens to report issues
- **Maintenance Planning**: Prioritize repairs based on risk

## 🔐 Security

- Environment variables for sensitive API keys
- Firebase authentication for data access
- Secret file handling on Render
- No credentials committed to repository
- HTTPS encryption on Render

## 📦 Dependencies

```
Flask==3.0.0
Flask-CORS==4.0.0
firebase-admin==6.4.0
google-generativeai==0.7.0
Pillow==11.0.0
python-dotenv==1.0.0
```

## 🎓 Learning Outcomes

This project demonstrates:
- Full-stack web development (Frontend + Backend)
- AI/ML integration with Google Gemini
- Cloud deployment and scaling
- Image processing and optimization
- Real-time data management with Firebase
- REST API design
- Security best practices

## 🔄 Workflow

1. User uploads infrastructure damage image
2. Frontend compresses image for optimization
3. Captures location via geolocation API
4. Sends to backend API with image & metadata
5. Flask processes image and calls Gemini AI
6. AI analyzes damage and returns risk assessment
7. Report stored in Firebase with unique ID
8. Results displayed to user in real-time
9. User can provide feedback for model improvement

## 🚧 Future Enhancements

- [ ] Multiple image upload support
- [ ] Heat map visualization of damage hotspots
- [ ] Mobile app for iOS/Android
- [ ] Real-time notifications to authorities
- [ ] Historical damage tracking and trends
- [ ] Integration with city infrastructure databases
- [ ] ML model fine-tuning based on feedback
- [ ] Damage severity prediction timeline

## 👥 Contributors

- Aniket Walanj

## 📝 License

MIT License - Feel free to use and modify

## 🤝 Support

For issues or questions:
- GitHub Issues: [infra-tracker-v2](https://github.com/ankyagg/infra-tracker-v2/issues)
- Email: Contact via GitHub profile

## 🌐 Live Demo

**Frontend**: https://ankyagg.github.io/infra-tracker-v2/
**Backend API**: https://infra-tracker-v2.onrender.com

---

**Built with ❤️ for Infrastructure Management**
