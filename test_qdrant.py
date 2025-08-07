#!/usr/bin/env python3
"""
Test Qdrant connection
"""

import requests
import json

def test_qdrant():
    """Test if Qdrant is running and accessible"""
    
    qdrant_url = "http://localhost:6333"
    
    try:
        # Test basic connection
        response = requests.get(f"{qdrant_url}/")
        print(f"✅ Qdrant is running! Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Test collections endpoint
        response = requests.get(f"{qdrant_url}/collections")
        print(f"✅ Collections endpoint accessible! Status: {response.status_code}")
        collections = response.json()
        print(f"Existing collections: {collections}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Qdrant. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Error testing Qdrant: {e}")
        return False

if __name__ == "__main__":
    test_qdrant()
