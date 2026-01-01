from flask import Flask, request, jsonify, render_template
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import json
import uuid
from datetime import datetime
import logging

# Load environment variables from .env file
load_dotenv()

# ========== SIMPLE LOGGING ==========
import sys
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)
# ========== END LOGGING CONFIG ==========

# Create Flask app
app = Flask(__name__)

# ========== FALLBACK SOLUTION ==========
# Since your custom client has issues, let's use REQUESTS directly
import requests

supabase_url = "https://rzryozfztwupzjhlkwji.supabase.co"
supabase_key = "sb_publishable_kCre0WyunXL8XxrETcmsUw_wMhssuDA"

headers = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {supabase_key}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"  # Important for INSERT operations
}

def supabase_select(table, filters=None, limit=None):
    """Simple SELECT using requests library"""
    url = f"{supabase_url}/rest/v1/{table}"
    params = {}
    
    if filters:
        for key, value in filters.items():
            params[key] = f"eq.{value}"
    if limit:
        params["limit"] = str(limit)
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"SELECT error on {table}: {e}")
        return []

def supabase_insert(table, data):
    """Simple INSERT using requests library"""
    url = f"{supabase_url}/rest/v1/{table}"
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.error(f"INSERT error on {table}: {e}")
        logger.error(f"Response: {e.response.text}")
        raise

# Test connection
try:
    logger.debug("Testing Supabase connection...")
    test_data = supabase_select("users", limit=1)
    logger.debug(f"✅ Connection test: Found {len(test_data)} users")
    db_connected = True
except Exception as e:
    logger.error(f"❌ Connection failed: {e}")
    db_connected = False
# ========== END FALLBACK SOLUTION ==========

# Homepage
@app.route('/')
def home():
    mode = "mock" if not db_connected else "real"
    return f"BAPA API is running! ({mode.title()} Mode)"

# Test environment variables
@app.route('/test-env')
def test_env():
    mode = "mock" if not db_connected else "real"
    return jsonify({
        "supabase_url": os.getenv("SUPABASE_URL"),
        "anon_key_exists": bool(os.getenv("SUPABASE_ANON_KEY")),
        "service_key_exists": bool(os.getenv("SUPABASE_SERVICE_KEY")),
        "status": "success",
        "mode": mode,
        "database_connected": db_connected
    })

# Test database connection
@app.route('/test-db')
def test_db():
    if not db_connected:
        return jsonify({
            "status": "mock",
            "message": "Mock mode - Supabase not connected",
            "data": [],
            "mode": "mock"
        })
    
    try:
        data = supabase_select("users", limit=10)
        return jsonify({
            "status": "success",
            "message": f"Database connected! Found {len(data)} users",
            "data": data,
            "mode": "real"
        })
    except Exception as e:
        logger.error(f"Database query failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Database query failed: {str(e)}",
            "data": [],
            "mode": "real"
        })

# ========== SIMPLE WORKING /api/submit ==========
@app.route('/api/submit', methods=['POST'])
def submit_test():
    logger.debug("=== /api/submit called ===")
    
    if not db_connected:
        return jsonify({
            "status": "mock",
            "message": "Mock mode - Database not connected",
            "api_key": f"bapa_mock_{uuid.uuid4().hex[:8]}",
            "mode": "mock"
        })
    
    try:
        data = request.json or {}
        
        # 1. Check or create user
        user_email = data.get('email', f"user_{uuid.uuid4().hex[:8]}@bapa.com")
        logger.debug(f"Processing user: {user_email}")
        
        # Check if user exists
        existing_users = supabase_select("users", {"email": user_email})
        
        if existing_users:
            user_id = existing_users[0]['id']
            logger.debug(f"User exists: {user_id}")
        else:
            # Create new user
            logger.debug(f"Creating new user: {user_email}")
            new_user = supabase_insert("users", {"email": user_email})
            user_id = new_user[0]['id'] if new_user else str(uuid.uuid4())
            logger.debug(f"Created user with ID: {user_id}")
        
        # 2. Create a simple response record
        response_data = {
            "user_id": user_id,
            "sovereignty_score": data.get('sovereignty_score', 75.5),
            "answers": data.get('answers', {}),
            "profile": data.get('profile', {}),
            "oce_matrix": data.get('oce_matrix', {}),
            "language": data.get('language', 'EN')
        }
        
        logger.debug(f"Inserting response data")
        response_result = supabase_insert("responses", response_data)
        response_id = response_result[0]['id'] if response_result else str(uuid.uuid4())
        
        # 3. Generate API key
        api_key = f"bapa_{uuid.uuid4().hex}"
        api_key_data = {
            "user_id": user_id,
            "api_key": api_key,
            "is_active": True,
            "requests_count": 0
        }
        
        logger.debug(f"Creating API key: {api_key[:10]}...")
        supabase_insert("api_keys", api_key_data)
        
        # SUCCESS!
        return jsonify({
            "status": "success",
            "message": "BAPA test saved successfully!",
            "user_id": user_id,
            "response_id": response_id,
            "api_key": api_key,
            "sovereignty_score": response_data['sovereignty_score'],
            "profile_type": response_data['profile'].get('type', 'Not specified'),
            "mode": "real",
            "next_steps": [
                "Use this API key to access your profile",
                "Endpoint: GET /api/v1/profile",
                "Header: Authorization: Bearer YOUR_API_KEY"
            ]
        })
        
    except Exception as e:
        logger.error(f"ERROR in /api/submit: {str(e)}", exc_info=True)
        
        # Return error with details
        return jsonify({
            "error": str(e),
            "error_type": type(e).__name__,
            "debug_info": {
                "db_connected": db_connected,
                "has_request_data": request.json is not None
            }
        }), 500

# Get profile using API key
@app.route('/api/v1/profile', methods=['GET'])
def get_profile():
    try:
        # Get API key from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        
        api_key = auth_header.split(' ')[1]
        
        if not db_connected:
            # Mock mode
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
                "mode": "mock"
            })
        
        # REAL MODE: Verify API key exists
        api_keys = supabase_select("api_keys", {"api_key": api_key, "is_active": "true"})
        
        if not api_keys:
            return jsonify({"error": "Invalid or inactive API key"}), 401
        
        api_key_data = api_keys[0]
        user_id = api_key_data['user_id']
        
        # Get user info
        users = supabase_select("users", {"id": user_id})
        if not users:
            return jsonify({"error": "User not found"}), 404
        
        # Get latest response
        responses = supabase_select("responses", {"user_id": user_id})
        if not responses:
            return jsonify({"error": "No test results found"}), 404
        
        # Get latest response
        latest_response = max(responses, key=lambda x: x.get('created_at', ''))
        
        return jsonify({
            "user_id": user_id,
            "email": users[0]['email'],
            "sovereignty_score": latest_response.get('sovereignty_score', 75.5),
            "profile_type": latest_response.get('profile', {}).get('type', 'Operator'),
            "strengths": latest_response.get('profile', {}).get('strengths', ['Analytical Thinking', 'Problem Solving']),
            "weaknesses": latest_response.get('profile', {}).get('weaknesses', ['Time Management', 'Detail Orientation']),
            "communication_style": latest_response.get('profile', {}).get('communication_style', 'Direct and concise'),
            "oce_matrix": latest_response.get('oce_matrix', {}),
            "last_updated": latest_response.get('created_at', datetime.now().isoformat()),
            "api_requests_used": api_key_data.get('requests_count', 0) + 1,
            "api_requests_limit": 1000,
            "mode": "real"
        })
        
    except Exception as e:
        logger.error(f"Error in /api/v1/profile: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# Main function to run the app
if __name__ == '__main__':
    mode = "mock" if not db_connected else "real"
    
    logger.info("=" * 50)
    logger.info(f"🚀 BAPA API Server - {mode.upper()} MODE")
    logger.info("=" * 50)
    logger.info(f"📊 Supabase URL: {supabase_url}")
    logger.info(f"🔑 Anon Key: Loaded")
    logger.info(f"🗄️ Database: {'✅ Connected' if db_connected else '❌ Not Connected'}")
    logger.info("=" * 50)
    logger.info(f"🌐 Server running on: http://localhost:5000")
    logger.info("🔗 Available Endpoints:")
    logger.info("   - GET  /                    - Homepage")
    logger.info("   - GET  /test-env            - Test environment")
    logger.info("   - GET  /test-db             - Test database")
    logger.info("   - POST /api/submit          - Submit BAPA test")
    logger.info("   - GET  /api/v1/profile      - Get profile (requires API key)")
    logger.info("=" * 50)
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)