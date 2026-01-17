
from dotenv import load_dotenv

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from datetime import timedelta, timezone

load_dotenv()

# Serve static files from the parent directory (../)
app = Flask(__name__, static_folder="../", static_url_path="")
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # Allow up to 20MB uploads

# IST timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))