from flask import Flask, request, jsonify, render_template
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import json
import uuid
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Create Flask app
app = Flask(__name__)

# DEBUG: Show what Railway provides
print("=== RAILWAY ENV DEBUG ===")
print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
print(f"SUPABASE_ANON_KEY exists: {bool(os.getenv('SUPABASE_ANON_KEY'))}")
print(f"SUPABASE_ANON_KEY first 30 chars: {os.getenv('SUPABASE_ANON_KEY')[:30] if os.getenv('SUPABASE_ANON_KEY') else 'None'}")
print("=========================")

# MOCK MODE: Skip Supabase for now
print("⚠️ MOCK MODE: Supabase disabled for testing")
supabase = None

# Homepage
@app.route('/')
def home():
    return "BAPA API is running! (Mock Mode)"

# Test environment variables
@app.route('/test-env')
def test_env():
    return jsonify({
        "supabase_url": os.getenv("SUPABASE_URL"),
        "anon_key_exists": bool(os.getenv("SUPABASE_ANON_KEY")),
        "service_key_exists": bool(os.getenv("SUPABASE_SERVICE_KEY")),
        "status": "success",
        "mode": "mock"
    })

# Test database connection (mock)
@app.route('/test-db')
def test_db():
    return jsonify({
        "status": "success",
        "message": "Mock mode - Supabase temporarily disabled",
        "data": [],
        "mode": "mock"
    })

# Submit BAPA test results (mock)
@app.route('/api/submit', methods=['POST'])
def submit_test():
    try:
        data = request.json
        
        # Generate mock response
        mock_response = {
            "status": "success",
            "message": "Mock mode - Test saved (not really in database)",
            "user_id": str(uuid.uuid4()),
            "response_id": str(uuid.uuid4()),
            "api_key": f"bapa_mock_{uuid.uuid4().hex[:8]}",
            "sovereignty_score": data.get('sovereignty_score', 75.5),
            "profile_type": data.get('profile', {}).get('type', 'Operator'),
            "next_steps": [
                "This is a mock response - no data saved to database",
                "Fix Supabase connection to enable real saving"
            ],
            "mode": "mock"
        }
        
        return jsonify(mock_response)
        
    except Exception as e:
        return jsonify({"error": str(e), "mode": "mock"}), 500

# Get profile using API key (mock)
@app.route('/api/v1/profile', methods=['GET'])
def get_profile():
    try:
        # Get API key from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                "error": "Missing or invalid Authorization header",
                "mode": "mock"
            }), 401
        
        api_key = auth_header.split(' ')[1]
        
        # Return mock profile
        return jsonify({
            "user_id": str(uuid.uuid4()),
            "email": "mock_user@example.com",
            "sovereignty_score": 85.0,
            "profile_type": "Synthesizer",
            "strengths": ["Analytical Thinking", "Problem Solving"],
            "weaknesses": ["Time Management", "Detail Orientation"],
            "communication_style": "Direct and concise",
            "oce_matrix": {"openness": 0.8, "conscientiousness": 0.6},
            "last_updated": datetime.now().isoformat(),
            "api_requests_used": 1,
            "api_requests_limit": 1000,
            "mode": "mock",
            "note": "This is mock data - fix Supabase connection for real data"
        })
        
    except Exception as e:
        return jsonify({"error": str(e), "mode": "mock"}), 500

# Main function to run the app
if __name__ == '__main__':
    print("=" * 50)
    print("🚀 BAPA API Server - MOCK MODE")
    print("=" * 50)
    print(f"📊 Supabase URL: {os.getenv('SUPABASE_URL')}")
    print(f"🔑 Anon Key: {'✅ Loaded' if os.getenv('SUPABASE_ANON_KEY') else '❌ Missing'}")
    print(f"🔐 Service Key: {'✅ Loaded' if os.getenv('SUPABASE_SERVICE_KEY') else '❌ Missing'}")
    print("=" * 50)
    print("⚠️ RUNNING IN MOCK MODE - No database connection")
    print("🌐 Server running on: http://localhost:5000")
    print("🔗 Available Endpoints (all return mock data):")
    print("   - GET  /                    - Homepage")
    print("   - GET  /test-env            - Test environment")
    print("   - GET  /test-db             - Test database (mock)")
    print("   - POST /api/submit          - Submit BAPA test (mock)")
    print("   - GET  /api/v1/profile      - Get profile (mock)")
    print("=" * 50)
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)