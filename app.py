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

# ========== SIMPLE SUPABASE CLIENT (FIXED) ==========
import requests

supabase_url = "https://rzryozfztwupzjhlkwji.supabase.co"
supabase_key = "sb_publishable_kCre0WyunXL8XxrETcmsUw_wMhssuDA"

class SimpleSupabaseClient:
    def __init__(self, url, key):
        self.base_url = url
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        logger.debug(f"Supabase client initialized for URL: {url}")
    
    def table(self, table_name):
        return SimpleTableClient(f"{self.base_url}/rest/v1/{table_name}", self.headers)

class SimpleTableClient:
    def __init__(self, endpoint, headers):
        self.endpoint = endpoint
        self.headers = headers
    
    def select(self, columns="*"):
        self.select_columns = columns
        return self
    
    def eq(self, column, value):
        if not hasattr(self, 'params'):
            self.params = {}
        self.params[column] = f"eq.{value}"
        return self
    
    def limit(self, count):
        if not hasattr(self, 'params'):
            self.params = {}
        self.params['limit'] = str(count)
        return self
    
    def execute(self):
        try:
            import urllib.request
            import urllib.parse
            
            # Build URL with params
            url = self.endpoint
            if hasattr(self, 'params'):
                url += '?' + urllib.parse.urlencode(self.params)
            
            logger.debug(f"Making GET request to: {url}")
            
            # Create request
            req = urllib.request.Request(url, headers=self.headers)
            
            # Make request
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
            
            class Response:
                def __init__(self, data):
                    self.data = data
            
            logger.debug(f"GET request successful, got {len(data)} items")
            return Response(data)
            
        except Exception as e:
            logger.error(f"GET request failed: {str(e)}")
            raise
    
    def insert(self, data):
        try:
            import urllib.request
            import json
            
            logger.debug(f"Making POST request to: {self.endpoint}")
            logger.debug(f"Data to insert: {data}")
            
            # Create request
            req = urllib.request.Request(
                self.endpoint,
                data=json.dumps(data).encode('utf-8'),
                headers=self.headers,
                method='POST'
            )
            
            # Make request
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode())
            
            class Response:
                def __init__(self, data):
                    self.data = data
            
            logger.debug(f"POST request successful: {result}")
            return Response(result)
            
        except Exception as e:
            logger.error(f"POST request failed: {str(e)}")
            # Return the actual error
            raise

try:
    supabase = SimpleSupabaseClient(supabase_url, supabase_key)
    logger.debug("✅ Simple REST client created")
    
    # Test connection
    test_response = supabase.table('users').select('*').limit(1).execute()
    logger.debug(f"✅ Database connection test: {len(test_response.data)} users found")
    
except Exception as e:
    logger.error(f"⚠️ REST API initialization error: {e}", exc_info=True)
    supabase = None
# ========== END CLIENT SECTION ==========

# Homepage
@app.route('/')
def home():
    mode = "mock" if supabase is None else "real"
    return f"BAPA API is running! ({mode.title()} Mode)"

# Test environment variables
@app.route('/test-env')
def test_env():
    mode = "mock" if supabase is None else "real"
    return jsonify({
        "supabase_url": os.getenv("SUPABASE_URL"),
        "anon_key_exists": bool(os.getenv("SUPABASE_ANON_KEY")),
        "service_key_exists": bool(os.getenv("SUPABASE_SERVICE_KEY")),
        "status": "success",
        "mode": mode,
        "database_connected": supabase is not None
    })

# Test database connection
@app.route('/test-db')
def test_db():
    if supabase is None:
        return jsonify({
            "status": "mock",
            "message": "Mock mode - Supabase not connected",
            "data": [],
            "mode": "mock"
        })
    
    try:
        response = supabase.table('users').select('*').limit(10).execute()
        return jsonify({
            "status": "success",
            "message": f"Database connected! Found {len(response.data)} users",
            "data": response.data,
            "mode": "real"
        })
    except Exception as e:
        logger.error(f"Database query failed: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": f"Database query failed: {str(e)}",
            "data": [],
            "mode": "real"
        })

# ========== SIMPLE TEST ENDPOINT ==========
@app.route('/api/submit', methods=['POST'])
def submit_test():
    logger.debug("=== /api/submit called ===")
    
    try:
        # Test 1: Basic connection
        logger.debug("Test 1: Checking supabase object")
        if supabase is None:
            return jsonify({"error": "Database not connected"}), 500
        
        # Test 2: Simple SELECT (we know this works)
        logger.debug("Test 2: Testing SELECT query")
        select_test = supabase.table('users').select('*').limit(1).execute()
        logger.debug(f"SELECT test: Found {len(select_test.data)} users")
        
        # Test 3: Try a SIMPLE insert with minimal data
        logger.debug("Test 3: Testing INSERT with minimal data")
        
        # Use a simple test table if 'users' doesn't allow inserts
        test_email = f"simple_test_{uuid.uuid4().hex[:8]}@test.com"
        test_data = {"email": test_email}
        
        logger.debug(f"Attempting to insert: {test_data}")
        
        # Try the insert
        insert_result = supabase.table('users').insert(test_data).execute()
        logger.debug(f"Insert result: {insert_result.data}")
        
        # If we get here, it worked!
        return jsonify({
            "status": "success",
            "message": "All tests passed!",
            "select_test": f"Found {len(select_test.data)} users",
            "insert_test": f"Inserted user with ID: {insert_result.data[0]['id'] if insert_result.data else 'unknown'}",
            "test_email": test_email
        })
        
    except Exception as e:
        logger.error(f"ERROR in /api/submit: {str(e)}", exc_info=True)
        
        # Return detailed error
        import traceback
        error_trace = traceback.format_exc()
        
        return jsonify({
            "error": str(e),
            "error_type": type(e).__name__,
            "error_details": error_trace,
            "debug_info": {
                "supabase_connected": supabase is not None,
                "supabase_url": supabase_url
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
        
        if supabase is None:
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
        
        # REAL MODE: Verify API key exists and is active
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
            "api_requests_limit": 1000,
            "mode": "real"
        })
        
    except Exception as e:
        logger.error(f"Error in /api/v1/profile: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# Main function to run the app
if __name__ == '__main__':
    mode = "mock" if supabase is None else "real"
    
    logger.info("=" * 50)
    logger.info(f"🚀 BAPA API Server - {mode.upper()} MODE")
    logger.info("=" * 50)
    logger.info(f"📊 Supabase URL: {supabase_url}")
    logger.info(f"🔑 Anon Key: Loaded")
    logger.info(f"🗄️ Database: {'✅ Connected' if supabase is not None else '❌ Not Connected'}")
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