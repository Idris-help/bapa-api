import os
from supabase import create_client

# Use your anon key
key = "sb_publishable_kCre0WyunXL8XxrETcmsUw_wMhssuDA"
url = "https://rzryozfztwupzjhlkwji.supabase.co"

print(f"Testing anon key with RLS disabled...")
print(f"Key: {key[:30]}...")
print(f"URL: {url}")

try:
    client = create_client(url, key)
    print("✅ Client created")
    
    # Try to insert a user (should work with RLS disabled)
    test_email = f"test_{os.urandom(4).hex()}@example.com"
    data = {"email": test_email}
    
    response = client.table('users').insert(data).execute()
    print(f"✅ Insert successful! User ID: {response.data[0]['id']}")
    
    # Try to read
    users = client.table('users').select('*').execute()
    print(f"✅ Read successful! Found {len(users.data)} users")
    
except Exception as e:
    print(f"❌ Error: {e}")