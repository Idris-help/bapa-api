import requests
import json

# Test data
test_data = {
    "email": "test_user_e9b651c7@example.com",  # Your test user email
    "language": "EN",
    "answers": {
        "q1": 5, "q2": 4, "q3": 3, "q4": 5, "q5": 2,
        "q6": 4, "q7": 3, "q8": 5, "q9": 4, "q10": 3
    },
    "sovereignty_score": 78.5,
    "oce_matrix": {
        "openness": 0.8, "conscientiousness": 0.6,
        "extraversion": 0.4, "agreeableness": 0.7,
        "neuroticism": 0.3
    },
    "profile": {
        "type": "Synthesizer",
        "strengths": ["Strategic Thinking", "Problem Solving", "Adaptability"],
        "weaknesses": ["Time Management", "Detail Orientation"],
        "communication_style": "Direct and concise"
    }
}

print("Submitting BAPA test...")
try:
    response = requests.post(
        "http://localhost:5000/api/submit",
        json=test_data,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    print("Status Code:", response.status_code)
    print("Response:", json.dumps(response.json(), indent=2))
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ SUCCESS!")
        print(f"📋 Message: {data.get('message')}")
        print(f"🔑 API Key: {data.get('api_key')}")
        print(f"📊 Score: {data.get('sovereignty_score')}")
        print(f"👤 Profile: {data.get('profile_type')}")
        
        # Save the API key to a file for later use
        with open('test_api_key.txt', 'w') as f:
            f.write(data.get('api_key', ''))
        print("💾 API key saved to test_api_key.txt")
        
except requests.exceptions.ConnectionError:
    print("❌ Connection error - make sure Flask app is running!")
except Exception as e:
    print(f"❌ Error: {e}")