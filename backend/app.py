from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import os
import base64
from datetime import datetime, timezone, timedelta
import uuid
import google.generativeai as genai
from PIL import Image
from io import BytesIO
import json
from appwrite.client import Client
from appwrite.services.storage import Storage
from appwrite.input_file import InputFile
from dotenv import load_dotenv

load_dotenv()

# Serve static files from the parent directory (../)
app = Flask(__name__, static_folder="../", static_url_path="")
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # Allow up to 20MB uploads

# IST timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

# --- APPWRITE SETUP ---
APPWRITE_ENDPOINT = os.getenv("APPWRITE_ENDPOINT")
APPWRITE_PROJECT_ID = os.getenv("APPWRITE_PROJECT_ID")
APPWRITE_API_KEY = os.getenv("APPWRITE_API_KEY")
APPWRITE_BUCKET_ID = os.getenv("APPWRITE_BUCKET_ID")

appwrite_client = None
appwrite_storage = None

if all([APPWRITE_ENDPOINT, APPWRITE_PROJECT_ID, APPWRITE_API_KEY]):
    try:
        appwrite_client = Client()
        appwrite_client.set_endpoint(APPWRITE_ENDPOINT)
        appwrite_client.set_project(APPWRITE_PROJECT_ID)
        appwrite_client.set_key(APPWRITE_API_KEY)
        appwrite_storage = Storage(appwrite_client)
        print("Appwrite initialized successfully")
    except Exception as e:
        print(f"Error initializing Appwrite: {e}")
else:
    print("WARNING: Appwrite credentials not fully set")

# --- FIREBASE SETUP ---
firebase_key_path = "serviceAccountKey.json"  # Looks for this file in the backend folder
firebase_key_env = os.getenv("FIREBASE_KEY")

if firebase_key_env:
    firebase_key_dict = json.loads(firebase_key_env)
    cred = credentials.Certificate(firebase_key_dict)
elif os.path.exists(firebase_key_path):
    cred = credentials.Certificate(firebase_key_path)
else:
    print("WARNING: Firebase credentials not found.")
    cred = None

if cred:
    try:
        firebase_admin.initialize_app(cred)
        db = firestore.client()
    except ValueError:
        # App already initialized
        db = firestore.client()
else:
    db = None

# --- GEMINI SETUP ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ACTIVE_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

genai_client = None
if GEMINI_API_KEY:
    genai_client = genai.Client(api_key=GEMINI_API_KEY)
    print(f"Gemini initialized with model: {ACTIVE_GEMINI_MODEL}")
else:
    print("WARNING: GEMINI_API_KEY not configured")

# --- ROUTES ---

@app.route("/")
def index():
    return send_from_directory("../", "index.html")

# NEW: Route for Admin Dashboard to fetch reports
@app.route("/get-reports", methods=["GET"])
def get_reports():
    try:
        if not db:
            return jsonify({"status": "error", "message": "Database not connected"}), 500
            
        # Fetch reports ordered by newest first
        # Note: 'timestamp' is stored as ISO string, which sorts correctly alphabetically
        docs = db.collection("reports").order_by("timestamp", direction=firestore.Query.DESCENDING).stream()
        
        reports_list = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            reports_list.append(data)
            
        return jsonify({"status": "success", "reports": reports_list})
    except Exception as e:
        print(f"Error fetching reports: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# NEW: Route for Admin Dashboard to update status
@app.route("/update-report-status", methods=["POST"])
def update_report_status():
    try:
        data = request.json
        report_id = data.get("report_id")
        new_status = data.get("status")
        
        if not db:
            return jsonify({"status": "error", "message": "Database not connected"}), 500
            
        db.collection("reports").document(report_id).update({"status": new_status})
        
        return jsonify({"status": "success", "message": "Status updated"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/submit-report", methods=["POST"])
def submit_report():
    try:
        data = request.json
        print(f"Received report submission")

        category = data.get("category")
        description = data.get("description")
        location = data.get("location")
        image = data.get("image")  # base64 from frontend
        
        # Assess risk with Gemini
        risk_assessment = None
        if image and GEMINI_API_KEY:
            print("Analyzing with Gemini...")
            risk_assessment = assess_risk_with_gemini(image, category, description)
        
        # Upload to Appwrite Storage
        image_url = None
        if image and appwrite_storage and APPWRITE_BUCKET_ID:
            try:
                img_data = image.split(",")[1] if "," in image else image
                decoded_image = base64.b64decode(img_data)
                
                file_id = str(uuid.uuid4())
                appwrite_storage.create_file(
                    bucket_id=APPWRITE_BUCKET_ID,
                    file_id=file_id,
                    file=InputFile.from_bytes(decoded_image, filename=f"{file_id}.jpg")
                )
                image_url = f"{APPWRITE_ENDPOINT}/storage/buckets/{APPWRITE_BUCKET_ID}/files/{file_id}/view?project={APPWRITE_PROJECT_ID}"
            except Exception as e:
                print(f"Appwrite upload error: {e}")

        report = {
            "category": category,
            "description": description,
            "location": location,
            "image": image_url, 
            "risk_assessment": risk_assessment,
            "status": "Reported", # Default status
            "timestamp": datetime.now(IST).isoformat()
        }

        if db:
            result = db.collection("reports").add(report)
            report_id = result[1].id
            return jsonify({
                "status": "success", 
                "id": report_id, 
                "risk_assessment": risk_assessment
            })
        else:
             return jsonify({"status": "error", "message": "Firebase not configured"}), 500

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# --- HELPER FUNCTIONS ---

def assess_risk_with_gemini(image_base64, category, description):
    # (Kept your original logic here to save space, assuming it's correct)
    # Just ensure default_fallback is defined if you use it
    default_fallback = {
        "risk_level": 2, "urgency": "low", "damage_type": "Manual Review Needed",
        "recommended_actions": ["Inspect manually"]
    }
    
    try:
        if "," in image_base64: image_base64 = image_base64.split(",")[1]
        image_data = base64.b64decode(image_base64)
        image = Image.open(BytesIO(image_data))

        prompt = f"""
        Analyze this infrastructure damage image.
        Category: {category}. Description: {description}.
        Provide a JSON response with:
        - risk_level (1-5 int)
        - safety_risk (1-5 int)
        - urgency (immediate, high, medium, low)
        - damage_type (string)
        - recommended_actions (list of strings)
        RETURN ONLY JSON.
        """

        response = genai_client.models.generate_content(
            model=ACTIVE_GEMINI_MODEL,
            contents=[prompt, image]
        )
        
        # Basic JSON extraction logic
        text = response.text
        if "{" in text and "}" in text:
            json_str = text[text.find("{"):text.rfind("}")+1]
            return json.loads(json_str)
        return default_fallback
        
    except Exception as e:
        print(f"Gemini Error: {e}")
        return default_fallback

if __name__ == "__main__":
    # Default to 5000
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)