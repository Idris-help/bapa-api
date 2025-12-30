import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

key = "sb_publishable_kCre0WyunXL8XxrETcmsUw_wMhssuDA"
url = "https://rzryozfztwupzjhlkwji.supabase.co"

print(f"Testing key: {key[:30]}...")
print(f"URL: {url}")

try:
    client = create_client(url, key)
    print("✅ Key works locally!")
    
    # Try a simple query
    response = client.table('users').select('*').limit(1).execute()
    print(f"✅ Database query successful: {len(response.data)} rows")
    
except Exception as e:
    print(f"❌ Error: {e}")