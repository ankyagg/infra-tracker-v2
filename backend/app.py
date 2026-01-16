from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import os
import base64
from datetime import datetime, timezone, timedelta
import uuid
from google import genai
from PIL import Image
from io import BytesIO
import json
from appwrite.client import Client
from appwrite.services.storage import Storage
from appwrite.input_file import InputFile
from dotenv import load_dotenv
import hashlib
import secrets

load_dotenv()

# Serve static files from the parent directory (../)
app = Flask(__name__, static_folder="../", static_url_path="")
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # Allow up to 20MB uploads

# IST timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))


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
# Get the directory where app.py is located
script_dir = os.path.dirname(os.path.abspath(__file__))
firebase_key_path = os.path.join(script_dir, "serviceAccountKey.json")
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
        print("Firebase initialized successfully")
    except ValueError:
        # App already initialized
        db = firestore.client()
        print("Firebase already initialized")
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

# Proxy endpoint for Appwrite images (to bypass CORS/auth issues)
@app.route("/image/<file_id>")
def get_image(file_id):
    try:
        if not appwrite_storage or not APPWRITE_BUCKET_ID:
            return jsonify({"error": "Storage not configured"}), 500
        
        # Get file from Appwrite
        result = appwrite_storage.get_file_view(
            bucket_id=APPWRITE_BUCKET_ID,
            file_id=file_id
        )
        
        from flask import Response
        return Response(result, mimetype='image/jpeg')
    except Exception as e:
        print(f"Image proxy error: {e}")
        return jsonify({"error": str(e)}), 404

# --- AUTHENTICATION HELPERS ---
def hash_password(password):
    """Hash password with SHA-256 and salt"""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{hashed}"

def verify_password(password, stored_hash):
    """Verify password against stored hash"""
    try:
        salt, hashed = stored_hash.split(':')
        return hashlib.sha256((password + salt).encode()).hexdigest() == hashed
    except:
        return False

def generate_token():
    """Generate a secure session token"""
    return secrets.token_urlsafe(32)

def get_admin_whitelist():
    """Load admin whitelist from JSON file"""
    try:
        whitelist_path = os.path.join(script_dir, "admin_whitelist.json")
        with open(whitelist_path, 'r') as f:
            data = json.load(f)
            return [email.lower().strip() for email in data.get("admin_emails", [])]
    except Exception as e:
        print(f"Error loading admin whitelist: {e}")
        return []

def is_admin_email(email):
    """Check if email is in admin whitelist"""
    whitelist = get_admin_whitelist()
    return email.lower().strip() in whitelist

# Store active tokens (in production, use Redis or database)
active_tokens = {}

# --- AUTHENTICATION ROUTES ---
@app.route("/auth/signup", methods=["POST"])
def auth_signup():
    try:
        data = request.json
        email = data.get("email", "").lower().strip()
        password = data.get("password", "")
        name = data.get("name", "").strip()
        
        if not email or not password or not name:
            return jsonify({"status": "error", "message": "All fields are required"}), 400
        
        if len(password) < 6:
            return jsonify({"status": "error", "message": "Password must be at least 6 characters"}), 400
        
        if not db:
            return jsonify({"status": "error", "message": "Database not connected"}), 500
        
        # Check if email already exists in users collection
        existing_user = db.collection("users").where("email", "==", email).limit(1).stream()
        if any(existing_user):
            return jsonify({"status": "error", "message": "Email already registered"}), 400
        
        # Determine role based on whitelist
        role = "admin" if is_admin_email(email) else "user"
        
        # Create user in users collection (all users stored here)
        user_data = {
            "email": email,
            "password": hash_password(password),
            "name": name,
            "role": role,
            "created_at": datetime.now(IST).isoformat()
        }
        
        db.collection("users").add(user_data)
        
        if role == "admin":
            return jsonify({"status": "success", "message": "Admin account created successfully"})
        else:
            return jsonify({"status": "success", "message": "Account created successfully. Note: You have user access only."})
        
    except Exception as e:
        print(f"Signup error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/auth/login", methods=["POST"])
def auth_login():
    try:
        data = request.json
        email = data.get("email", "").lower().strip()
        password = data.get("password", "")
        
        if not email or not password:
            return jsonify({"status": "error", "message": "Email and password required"}), 400
        
        if not db:
            return jsonify({"status": "error", "message": "Database not connected"}), 500
        
        user_doc = None
        user_data = None
        
        # Find user in users collection
        users = db.collection("users").where("email", "==", email).limit(1).stream()
        for doc in users:
            user_doc = doc
            user_data = doc.to_dict()
            break
        
        if not user_data:
            return jsonify({"status": "error", "message": "Invalid email or password"}), 401
        
        # Verify password
        if not verify_password(password, user_data.get("password", "")):
            return jsonify({"status": "error", "message": "Invalid email or password"}), 401
        
        # Get role from user data
        role = user_data.get("role", "user")
        
        # Update last_logged_in timestamp
        db.collection("users").document(user_doc.id).update({
            "last_logged_in": datetime.now(IST).isoformat()
        })
        
        # Generate session token
        token = generate_token()
        active_tokens[token] = {
            "email": email,
            "name": user_data.get("name", "User"),
            "user_id": user_doc.id,
            "role": role,
            "created_at": datetime.now(IST).isoformat()
        }
        
        return jsonify({
            "status": "success",
            "token": token,
            "name": user_data.get("name", "User"),
            "email": email,
            "role": role
        })
        
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/auth/verify", methods=["POST"])
def auth_verify():
    """Verify if a token is valid"""
    try:
        data = request.json
        token = data.get("token", "")
        
        if token in active_tokens:
            return jsonify({
                "status": "success",
                "valid": True,
                "user": active_tokens[token]
            })
        else:
            return jsonify({"status": "error", "valid": False}), 401
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/auth/logout", methods=["POST"])
def auth_logout():
    """Logout and invalidate token"""
    try:
        data = request.json
        token = data.get("token", "")
        
        if token in active_tokens:
            del active_tokens[token]
        
        return jsonify({"status": "success", "message": "Logged out successfully"})
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

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
        
        # Assess risk with Gemini FIRST (before uploading, so we have base64)
        risk_assessment = None
        if image and genai_client:
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
                # Use our proxy endpoint instead of direct Appwrite URL
                image_url = f"/image/{file_id}"
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
        pil_image = Image.open(BytesIO(image_data))
        
        # Convert image to bytes for Gemini API
        img_byte_arr = BytesIO()
        pil_image.save(img_byte_arr, format='JPEG')
        img_bytes = img_byte_arr.getvalue()

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
        
        print(f"Sending to Gemini - Model: {ACTIVE_GEMINI_MODEL}, Image size: {len(img_bytes)} bytes")

        # Use the correct format for google-genai library - pass PIL Image directly
        response = genai_client.models.generate_content(
            model=ACTIVE_GEMINI_MODEL,
            contents=[prompt, pil_image]
        )
        
        print(f"Gemini raw response: {response.text}")
        
        text = response.text
        if "{" in text and "}" in text:
            json_str = text[text.find("{"):text.rfind("}")+1]
            result = json.loads(json_str)
            print(f"Parsed result: {result}")
            return result
        print("No JSON found in response")
        return default_fallback
        
    except Exception as e:
        error_msg = str(e)
        print(f"Gemini Error: {type(e).__name__}: {e}")
        
        # Check for quota exceeded error
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg or "quota" in error_msg.lower():
            return {
                "risk_level": 0, 
                "urgency": "pending", 
                "damage_type": "AI Quota Exceeded - Manual Review Required",
                "recommended_actions": ["AI service quota exceeded. Please review manually or try again later."],
                "error": "API quota exceeded"
            }
        
        import traceback
        traceback.print_exc()
        return default_fallback

if __name__ == "__main__":
    # Default to 5000
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)