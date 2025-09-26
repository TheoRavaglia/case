import requests
import json

def test_render_api(base_url):
    """Test the deployed API on Render"""
    print(f"🚀 Testing API at: {base_url}")
    print("=" * 50)
    
    # Test 1: Root endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Root endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
    
    print("-" * 30)
    
    # Test 2: Login endpoint
    try:
        login_data = {
            "email": "admin@company.com",
            "password": "admin123"
        }
        response = requests.post(f"{base_url}/api/login", json=login_data)
        print(f"✅ Login endpoint: {response.status_code}")
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"   Token received: {token[:20]}...")
            return token
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Login failed: {e}")
    
    print("-" * 30)
    
    # Test 3: Docs endpoint
    try:
        response = requests.get(f"{base_url}/docs")
        print(f"✅ Docs endpoint: {response.status_code}")
        print(f"   FastAPI docs available at: {base_url}/docs")
    except Exception as e:
        print(f"❌ Docs failed: {e}")
    
    return None

if __name__ == "__main__":
    # Replace with your actual Render URL
    render_url = input("Cole a URL do seu Render (ex: https://marketing-analytics-api-xxxx.onrender.com): ")
    render_url = render_url.strip()
    
    if render_url:
        test_render_api(render_url)
    else:
        print("❌ URL não fornecida")