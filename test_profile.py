import requests
import json

# Read the API key from file
try:
    with open('test_api_key.txt', 'r') as f:
        API_KEY = f.read().strip()
    
    print(f"Using API key: {API_KEY[:20]}...")
    
    print("\nTesting profile API...")
    response = requests.get(
        "http://localhost:5000/api/v1/profile",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        timeout=10
    )
    
    print("Status Code:", response.status_code)
    print("Response:", json.dumps(response.json(), indent=2))
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ PROFILE RETRIEVED!")
        print(f"👤 Email: {data.get('email')}")
        print(f"📊 Sovereignty Score: {data.get('sovereignty_score')}")
        print(f"🎯 Profile Type: {data.get('profile_type')}")
        print(f"💪 Strengths: {', '.join(data.get('strengths', []))}")
        print(f"📈 API Requests Used: {data.get('api_requests_used')}")
        
except FileNotFoundError:
    print("❌ test_api_key.txt not found")
    print("Run test_submit.py first to generate an API key")
except Exception as e:
    print(f"❌ Error: {e}")