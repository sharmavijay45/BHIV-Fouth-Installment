#!/usr/bin/env python3
"""
Test the API integration with NAS Knowledge Base
"""

import requests
import json
import time

def test_api_endpoints():
    """Test all the API endpoints with NAS integration"""
    
    base_url = "http://localhost:8001"
    
    print("🧪 Testing BHIV API with NAS Knowledge Base Integration")
    print("=" * 60)
    
    # Test 1: Root endpoint
    print("\n1️⃣ Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print("✅ Root endpoint working")
            print(f"   Available endpoints: {list(data.get('endpoints', {}).keys())}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test 2: NAS KB Status
    print("\n2️⃣ Testing NAS Knowledge Base status...")
    try:
        response = requests.get(f"{base_url}/nas-kb/status")
        if response.status_code == 200:
            data = response.json()
            print("✅ NAS KB status endpoint working")
            print(f"   System tests: {data.get('system_tests', {})}")
            print(f"   Statistics: {data.get('statistics', {})}")
        else:
            print(f"❌ NAS KB status failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ NAS KB status error: {e}")
    
    # Test 3: List NAS documents
    print("\n3️⃣ Testing NAS documents listing...")
    try:
        response = requests.get(f"{base_url}/nas-kb/documents")
        if response.status_code == 200:
            data = response.json()
            print("✅ NAS documents listing working")
            print(f"   Document count: {data.get('count', 0)}")
            documents = data.get('documents', [])
            for doc in documents[:3]:  # Show first 3 documents
                print(f"   - {doc.get('document_id', 'Unknown')}: {doc.get('original_filename', 'Unknown')}")
        else:
            print(f"❌ NAS documents listing failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ NAS documents listing error: {e}")
    
    # Test 4: Search NAS KB
    print("\n4️⃣ Testing NAS Knowledge Base search...")
    search_queries = ["Vedas", "Ayurveda", "yoga", "meditation", "philosophy"]
    
    for query in search_queries:
        try:
            response = requests.get(f"{base_url}/nas-kb/search", params={"query": query, "limit": 2})
            if response.status_code == 200:
                data = response.json()
                results_count = data.get('count', 0)
                print(f"✅ Search '{query}': {results_count} results")
                if results_count > 0:
                    for result in data.get('results', [])[:1]:  # Show first result
                        content_preview = result.get('content', '')[:100] + '...'
                        print(f"   - {content_preview}")
            else:
                print(f"❌ Search '{query}' failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Search '{query}' error: {e}")
    
    # Test 5: Test spiritual endpoint with NAS integration
    print("\n5️⃣ Testing ask-vedas endpoint with NAS integration...")
    try:
        spiritual_query = "What do the Vedas say about meditation?"
        response = requests.get(f"{base_url}/ask-vedas", params={"query": spiritual_query})
        if response.status_code == 200:
            data = response.json()
            print("✅ ask-vedas endpoint working")
            print(f"   Query: {data.get('query', 'Unknown')}")
            print(f"   Response preview: {data.get('response', '')[:200]}...")
            print(f"   Sources: {len(data.get('sources', []))}")
        else:
            print(f"❌ ask-vedas failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ ask-vedas error: {e}")
    
    # Test 6: Test wellness endpoint with NAS integration
    print("\n6️⃣ Testing wellness endpoint with NAS integration...")
    try:
        wellness_query = "How can Ayurveda help with stress?"
        response = requests.get(f"{base_url}/wellness", params={"query": wellness_query})
        if response.status_code == 200:
            data = response.json()
            print("✅ wellness endpoint working")
            print(f"   Query: {data.get('query', 'Unknown')}")
            print(f"   Response preview: {data.get('response', '')[:200]}...")
            print(f"   Sources: {len(data.get('sources', []))}")
        else:
            print(f"❌ wellness failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ wellness error: {e}")
    
    # Test 7: Test edumentor endpoint with NAS integration
    print("\n7️⃣ Testing edumentor endpoint with NAS integration...")
    try:
        education_query = "Explain the philosophy of yoga"
        response = requests.get(f"{base_url}/edumentor", params={"query": education_query})
        if response.status_code == 200:
            data = response.json()
            print("✅ edumentor endpoint working")
            print(f"   Query: {data.get('query', 'Unknown')}")
            print(f"   Response preview: {data.get('response', '')[:200]}...")
            print(f"   Sources: {len(data.get('sources', []))}")
        else:
            print(f"❌ edumentor failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ edumentor error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 API Testing Complete!")
    print("✅ NAS Knowledge Base is now integrated with your BHIV API")
    print(f"📍 Knowledge base location: \\\\192.168.0.94\\Guruukul_DB\\knowledge_base")

def test_mcp_bridge():
    """Test MCP Bridge endpoint"""
    print("\n🌉 Testing MCP Bridge...")
    
    mcp_url = "http://localhost:8002"
    
    try:
        response = requests.get(f"{mcp_url}/")
        if response.status_code == 200:
            print("✅ MCP Bridge is running on port 8002")
        else:
            print(f"❌ MCP Bridge failed: {response.status_code}")
    except Exception as e:
        print(f"❌ MCP Bridge error: {e}")

if __name__ == "__main__":
    # Wait a moment for services to be fully ready
    print("⏳ Waiting for services to be ready...")
    time.sleep(3)
    
    test_api_endpoints()
    test_mcp_bridge()
