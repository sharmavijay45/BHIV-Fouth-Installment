#!/usr/bin/env python3
"""
Test script to verify the updated API works with Ollama
"""
import requests
import json

def test_api_endpoint():
    """Test the ask-vedas endpoint"""
    api_url = "http://localhost:8000/ask-vedas"
    
    payload = {
        "query": "What is the meaning of life?",
        "user_id": "test_user"
    }
    
    try:
        print("Testing API endpoint...")
        print(f"URL: {api_url}")
        print(f"Query: {payload['query']}")
        
        response = requests.post(
            api_url,
            json=payload,
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            print(f"Response: {result.get('response', '')[:200]}...")
            print(f"Sources: {len(result.get('sources', []))} sources found")
            print(f"Status: {result.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Error: Request timed out")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: Request failed - {e}")
        return False
    except Exception as e:
        print(f"❌ Error: Unexpected error - {e}")
        return False

if __name__ == "__main__":
    success = test_api_endpoint()
    if success:
        print("\n✅ API test passed!")
    else:
        print("\n❌ API test failed!")
