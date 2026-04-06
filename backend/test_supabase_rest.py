import requests
import os

# Manual parse of .env since we can't install python-dotenv easily
def load_env(path):
    env = {}
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            key, value = line.split('=', 1)
            env[key] = value
    return env

def test_supabase():
    env = load_env('.env')
    url = env.get('SUPABASE_URL')
    key = env.get('SUPABASE_SERVICE_KEY')
    
    print(f"Testing Supabase REST API at {url}...")
    
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}"
    }
    
    try:
        # Try to list tables or just a simple health check via an empty query on a likely table
        # or just hit the root API
        response = requests.get(f"{url}/rest/v1/", headers=headers, timeout=10)
        if response.status_code == 200:
            print("SUCCESS: Supabase REST API is reachable!")
        else:
            print(f"FAILURE: Supabase REST API returned status {response.status_code}")
            print(response.text)
            
        # Try a simple select 1 equivalent if possible, or just check connectivity
        # To check actual DB connectivity through PostgREST
        response = requests.get(f"{url}/rest/v1/rpc/get_size_by_table", headers=headers, timeout=10)
        # Note: get_size_by_table might not exist, but we just want to see if we get a 200 or 404 (reachable) 
        # vs a network error.
        print(f"RPC test status: {response.status_code}")
        
    except Exception as e:
        print(f"ERROR: Could not reach Supabase: {e}")

if __name__ == "__main__":
    test_supabase()
