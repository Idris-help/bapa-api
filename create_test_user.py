import os
from supabase import create_client
from dotenv import load_dotenv
import uuid

load_dotenv()

# Connect to Supabase
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

# Create a test user
test_user = {
    "email": f"test_user_{uuid.uuid4().hex[:8]}@example.com"
}

print("Creating test user...")
response = supabase.table("users").insert(test_user).execute()

print("✅ User created successfully!")
print("User ID:", response.data[0]['id'])
print("Email:", response.data[0]['email'])

# Save the user ID for later
user_id = response.data[0]['id']
print(f"\n📝 Save this user_id for testing: {user_id}")