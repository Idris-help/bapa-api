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

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("sb_secret_HqiTjHYw18X0WZAoI6XxDA_ReTo82lD")
)

# Homepage
@app.route('/')
def home():
    return "BAPA API is running! Database connection ready."

# Test environment variables
@app.route('/test-env')
def test_env():
    return jsonify({
        "supabase_url": os.getenv("SUPABASE_URL"),
        "anon_key_exists": bool(os.getenv("SUPABASE_ANON_KEY")),
        "service_key_exists": bool(os.getenv("SUPABASE_SERVICE_KEY")),
        "status": "success"
    })

# Test database connection
@app.route('/test-db')
def test_db():
    try:
        # Test reading from users table
        response = supabase.table('users').select('*').limit(10).execute()
        return jsonify({
            "status": "success",
            "message": f"Database connection successful! Found {len(response.data)} users.",
            "data": response.data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Submit BAPA test results - NOW SAVES TO DATABASE!
@app.route('/api/submit', methods=['POST'])
def submit_test():
    try:
        data = request.json
        
        # 1. Create user first (or use existing)
        user_email = data.get('email', f"user_{uuid.uuid4().hex[:8]}@bapa.com")
        
        # Check if user exists
        user_check = supabase.table('users').select('*').eq('email', user_email).execute()
        
        if user_check.data:
            # User exists
            user_id = user_check.data[0]['id']
        else:
            # Create new user
            user_data = {
                "email": user_email
            }
            user_response = supabase.table('users').insert(user_data).execute()
            user_id = user_response.data[0]['id']
        
        # 2. Save test response
        response_data = {
            "user_id": user_id,
            "language": data.get('language', 'EN'),
            "answers": data.get('answers', {}),
            "sovereignty_score": data.get('sovereignty_score', 75.5),
            "oce_matrix": data.get('oce_matrix', {}),
            "profile": data.get('profile', {})
        }
        
        response = supabase.table('responses').insert(response_data).execute()
        response_id = response.data[0]['id']
        
        # 3. Generate API key
        api_key = f"bapa_{uuid.uuid4().hex}"
        api_key_data = {
            "user_id": user_id,
            "api_key": api_key
        }
        
        supabase.table('api_keys').insert(api_key_data).execute()
        
        return jsonify({
            "status": "success",
            "message": "BAPA test saved successfully!",
            "user_id": user_id,
            "response_id": response_id,
            "api_key": api_key,
            "sovereignty_score": response_data['sovereignty_score'],
            "profile_type": response_data['profile'].get('type', 'Not specified'),
            "next_steps": [
                "Use this API key to access your profile",
                "Endpoint: GET /api/v1/profile",
                "Header: Authorization: Bearer YOUR_API_KEY"
            ]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get profile using API key
@app.route('/api/v1/profile', methods=['GET'])
def get_profile():
    try:
        # Get API key from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        
        api_key = auth_header.split(' ')[1]
        
        # Verify API key exists and is active
        key_check = supabase.table('api_keys').select('*, users(*)').eq('api_key', api_key).eq('is_active', True).execute()
        
        if not key_check.data:
            return jsonify({"error": "Invalid or inactive API key"}), 401
        
        api_key_data = key_check.data[0]
        user_id = api_key_data['user_id']
        
        # Get latest response for this user
        response_check = supabase.table('responses').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(1).execute()
        
        if not response_check.data:
            return jsonify({"error": "No test results found for this user"}), 404
        
        response_data = response_check.data[0]
        
        # Update request count
        supabase.table('api_keys').update({
            "requests_count": api_key_data['requests_count'] + 1
        }).eq('id', api_key_data['id']).execute()
        
        # Return profile
        return jsonify({
            "user_id": user_id,
            "email": api_key_data['users']['email'],
            "sovereignty_score": response_data['sovereignty_score'],
            "profile_type": response_data['profile'].get('type', 'Operator'),
            "strengths": response_data['profile'].get('strengths', ['Analytical Thinking', 'Problem Solving']),
            "weaknesses": response_data['profile'].get('weaknesses', ['Time Management', 'Detail Orientation']),
            "communication_style": response_data['profile'].get('communication_style', 'Direct and concise'),
            "oce_matrix": response_data['oce_matrix'],
            "last_updated": response_data['created_at'],
            "api_requests_used": api_key_data['requests_count'] + 1,
            "api_requests_limit": 1000
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Main function to run the app
if __name__ == '__main__':
    print("=" * 50)
    print("🚀 BAPA API Server - COMPLETE VERSION")
    print("=" * 50)
    print(f"📊 Supabase URL: {os.getenv('SUPABASE_URL')}")
    print(f"🔑 Anon Key: {'✅ Loaded' if os.getenv('SUPABASE_ANON_KEY') else '❌ Missing'}")
    print(f"🔐 Service Key: {'✅ Loaded' if os.getenv('SUPABASE_SERVICE_KEY') else '❌ Missing'}")
    print("=" * 50)
    print("🌐 Server running on: http://localhost:5000")
    print("🔗 Available Endpoints:")
    print("   - GET  /                    - Homepage")
    print("   - GET  /test-env            - Test environment")
    print("   - GET  /test-db             - Test database")
    print("   - POST /api/submit          - Submit BAPA test")
    print("   - GET  /api/v1/profile      - Get profile (requires API key)")
    print("=" * 50)
    
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)