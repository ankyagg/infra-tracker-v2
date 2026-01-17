import firebase_admin
from firebase_admin import credentials, firestore
import json

try:
    cred = credentials.Certificate('serviceAccountKey.json')
    try:
        firebase_admin.initialize_app(cred)
    except:
        pass
    
    db = firestore.client()
    docs = list(db.collection('reports').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1).stream())
    
    if docs:
        report = docs[0].to_dict()
        print('===== LATEST REPORT =====')
        print(f'Location: {report.get("location")}')
        print(f'Image URL: {report.get("image")}')
        print(f'Risk Assessment: {report.get("risk_assessment")}')
        print(f'Reporter Email: {report.get("reporter_email")}')
        print(f'Reporter Name: {report.get("reporter_name")}')
        print(f'Status: {report.get("status")}')
        print(f'Category: {report.get("category")}')
        print(f'Description: {report.get("description")}')
    else:
        print('No reports found')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
