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
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, static_folder="../", static_url_path="")
CORS(app)

# IST timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

# Initialize Firebase from environment variable or file
firebase_key_path = "backend/serviceAccountKey.json"
firebase_key_render_path = "/etc/secrets/serviceAccountKey.json"  # Render secret file path
firebase_key_env = os.getenv("FIREBASE_KEY")

if os.path.exists(firebase_key_render_path):
    # Load from Render secret file
    print("Loading Firebase from Render secret file")
    cred = credentials.Certificate(firebase_key_render_path)
elif firebase_key_env:
    # Load from environment variable
    firebase_key_dict = json.loads(firebase_key_env)
    cred = credentials.Certificate(firebase_key_dict)
elif os.path.exists(firebase_key_path):
    # Load from file (local development)
    cred = credentials.Certificate(firebase_key_path)
else:
    print("WARNING: Firebase credentials not found.")
    cred = None

if cred:
    firebase_admin.initialize_app(cred)
    db = firestore.client()
else:
    db = None

# Initialize Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")  # Free tier model
else:
    model = None
    print("WARNING: GEMINI_API_KEY environment variable not set")

@app.route("/")
def index():
    return send_from_directory("../", "index.html")

@app.route("/list-models", methods=["GET"])
def list_models():
    """List all available Gemini models"""
    try:
        if not GEMINI_API_KEY:
            return jsonify({
                "status": "error",
                "message": "API key not configured"
            }), 500
        
        models = genai.list_models()
        available_models = []
        
        for model in models:
            available_models.append({
                "name": model.name,
                "display_name": model.display_name,
                "supported_generation_methods": model.supported_generation_methods
            })
        
        return jsonify({
            "status": "success",
            "available_models": available_models,
            "total_models": len(available_models)
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/test-gemini", methods=["GET"])
def test_gemini():
    """Test if Gemini API is working"""
    try:
        if not model:
            return jsonify({
                "status": "error",
                "message": "Gemini API key not configured",
                "gemini_active": False
            }), 500
        
        # Test simple text generation
        test_response = model.generate_content("Say 'Gemini is working' in exactly those words.")
        
        if test_response and test_response.text:
            return jsonify({
                "status": "success",
                "message": "Gemini API is active and responding",
                "gemini_active": True,
                "test_response": test_response.text[:100]
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Gemini API returned empty response",
                "gemini_active": False
            }), 500
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Gemini API error: {str(e)}",
            "gemini_active": False,
            "error_details": str(e)
        }), 500

def assess_risk_with_gemini(image_base64, category, description):
    """
    Use Gemini to assess infrastructure damage risk from image
    """
    if not model:
        return {
            "risk_level": 3,
            "safety_risk": 3,
            "urgency": "medium",
            "assessment": "Gemini API not configured"
        }
    
    try:
        # Remove data URI prefix if present
        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]
        
        # Decode and convert to PIL Image
        image_data = base64.b64decode(image_base64)
        image = Image.open(BytesIO(image_data))
        
        # Create assessment prompt with detailed criteria
        prompt = """You are an expert infrastructure safety inspector with 20+ years experience. Analyze this damage image CAREFULLY and provide a DIFFERENTIATED risk assessment based on ACTUAL damage severity.

CRITICAL: Do NOT default to 3/5. Be precise and differentiated in your scoring.

ASSESSMENT SCALES:

Risk Level (1 to 5 scale):
1 = No visible damage or only cosmetic marks
2 = Minor damage (small cracks, surface wear, minor deterioration)
3 = Moderate damage (visible structural concerns, significant wear, needs attention soon)
4 = Severe damage (clear structural issues, significant risk, urgent repair needed)
5 = Critical damage (imminent danger, immediate closure and repair required)

Safety Risk (1 to 5 scale):
1 = No public safety risk whatsoever
2 = Minimal risk - only to people directly touching the damaged area
3 = Moderate risk - pedestrians or light traffic could be affected
4 = High risk - vehicles or pedestrians in area at significant injury risk
5 = Critical risk - immediate danger of severe injury or death

Urgency:
- immediate: Close area NOW, repair within hours (life-threatening)
- high: Repair within 24-48 hours (serious but not immediate danger)
- medium: Repair within 1-2 weeks (noticeable issue, needs attention)
- low: Schedule within 1 month (minor issue, monitor)

ANALYZE SPECIFIC DAMAGE INDICATORS:
- Look at actual damage extent (none, small, moderate, widespread)
- Assess structural integrity concerns
- Evaluate pedestrian/vehicle exposure
- Consider weather exposure and deterioration rate
- Identify specific hazards

RESPOND WITH ONLY THIS VALID JSON, NO OTHER TEXT:
{
  "risk_level": <1-5, NOT defaulting to 3>,
  "safety_risk": <1-5, NOT defaulting to 3>,
  "urgency": <immediate|high|medium|low>,
  "damage_type": "<specific type of damage observed>",
  "damage_extent": "<how widespread: none|minimal|localized|moderate|extensive>",
  "severity_justification": "<explain why you gave this specific risk level>",
  "identified_risks": ["<specific risk 1>", "<specific risk 2>", "<specific risk 3>"],
  "recommended_actions": ["<action 1>", "<action 2>", "<action 3>"]
}"""
        
        prompt += f"\n\nCategory: {category}\nUser Description: {description}\n\nBe SPECIFIC and DIFFERENTIATED. Do NOT give generic 3/5 scores. Analyze the actual damage."

        response = model.generate_content([prompt, image])
        response_text = response.text.strip()
        
        print(f"Raw Gemini response: {response_text[:500]}")
        
        # Extract JSON from response
        if "{" in response_text and "}" in response_text:
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            json_str = response_text[json_start:json_end]
            
            try:
                assessment = json.loads(json_str)
                
                # Validate and ensure proper scoring (don't default to 3)
                if "risk_level" not in assessment or assessment["risk_level"] is None:
                    assessment["risk_level"] = 2  # Default to lower if missing
                if "safety_risk" not in assessment or assessment["safety_risk"] is None:
                    assessment["safety_risk"] = 2
                
                # Ensure scores are in valid range
                assessment["risk_level"] = max(1, min(5, int(assessment.get("risk_level", 2))))
                assessment["safety_risk"] = max(1, min(5, int(assessment.get("safety_risk", 2))))
                
                assessment.setdefault("urgency", "medium")
                assessment.setdefault("damage_type", "Unknown damage")
                assessment.setdefault("damage_extent", "Unknown")
                assessment.setdefault("severity_justification", "")
                assessment.setdefault("identified_risks", [])
                assessment.setdefault("recommended_actions", [])
                
                # Ensure identified_risks and recommended_actions are lists
                if not isinstance(assessment["identified_risks"], list):
                    assessment["identified_risks"] = []
                if not isinstance(assessment["recommended_actions"], list):
                    assessment["recommended_actions"] = []
                
                print(f"Parsed assessment: {assessment}")
            except json.JSONDecodeError as e:
                print(f"JSON parse error: {str(e)}")
                assessment = {
                    "risk_level": 2,
                    "safety_risk": 2,
                    "urgency": "medium",
                    "damage_type": "Analysis failed",
                    "damage_extent": response_text[:200],
                    "severity_justification": "Failed to parse response",
                    "identified_risks": ["Unable to analyze image"],
                    "recommended_actions": ["Please resubmit image"]
                }
        else:
            print(f"No JSON found in response")
            assessment = {
                "risk_level": 2,
                "safety_risk": 2,
                "urgency": "medium",
                "damage_type": "Analysis error",
                "damage_extent": response_text[:200],
                "severity_justification": "Could not extract JSON",
                "identified_risks": ["Unable to analyze image"],
                "recommended_actions": ["Please resubmit image"]
            }
        
        return assessment
        
    except Exception as e:
        print(f"Gemini error: {str(e)}")
        return {
            "risk_level": 2,
            "safety_risk": 2,
            "urgency": "medium",
            "damage_type": "Analysis error",
            "damage_extent": "Error analyzing image",
            "severity_justification": "System error during analysis",
            "identified_risks": ["Unable to process image"],
            "recommended_actions": ["Please resubmit the image for analysis"],
            "error": str(e)
        }

@app.route("/submit-report", methods=["POST"])
def submit_report():
    try:
        data = request.json
        print(f"Received report submission")

        category = data.get("category")
        description = data.get("description")
        location = data.get("location")
        image = data.get("image")
        
        # Assess risk with Gemini if image provided
        risk_assessment = None
        if image and model:
            print("Analyzing with Gemini...")
            risk_assessment = assess_risk_with_gemini(image, category, description)
            print(f"Risk assessment: {risk_assessment}")
        
        report = {
            "category": category,
            "description": description,
            "location": location,
            "image": image,  # Store base64 image directly
            "risk_assessment": risk_assessment,  # Store AI analysis
            "timestamp": datetime.now(IST).isoformat()
        }

        if not db:
            return jsonify({
                "status": "error",
                "message": "Firebase not configured. Risk assessment: " + str(risk_assessment)
            }), 500
        
        result = db.collection("reports").add(report)
        report_id = result[1].id
        print(f"Report saved with ID: {report_id}")
        
        return jsonify({
            "status": "success",
            "id": report_id,
            "risk_assessment": risk_assessment
        })
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/submit-feedback", methods=["POST"])
def submit_feedback():
    """
    Store user feedback on risk assessments for AI improvement
    """
    try:
        data = request.json
        report_id = data.get("report_id")
        feedback_type = data.get("feedback_type")  # too-harsh, too-lenient, accurate
        feedback_comment = data.get("feedback_comment", "")
        
        if not report_id or not feedback_type:
            return jsonify({"status": "error", "message": "Missing report_id or feedback_type"}), 400
        
        # Store feedback in a separate collection
        feedback = {
            "report_id": report_id,
            "feedback_type": feedback_type,
            "comment": feedback_comment,
            "timestamp": datetime.now(IST).isoformat()
        }
        
        if db:
            db.collection("feedback").add(feedback)
            print(f"Feedback stored for report {report_id}: {feedback_type}")
        else:
            print(f"Firebase not configured. Feedback not stored for report {report_id}")
        
        return jsonify({
            "status": "success",
            "message": "Feedback recorded successfully"
        })
    except Exception as e:
        print(f"Feedback error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
