#!/usr/bin/env python3
"""
Test script to verify knowledge base integration
"""

import requests
import json

def test_wellness_endpoint():
    """Test the wellness endpoint with knowledge base integration."""
    print("🧪 [TEST] Testing wellness endpoint with knowledge base...")
    
    url = "http://localhost:8001/wellness"
    payload = {
        "query": "what is dharma",
        "user_id": "test_user"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ [SUCCESS] Status: {response.status_code}")
            print(f"📝 [RESPONSE] {result.get('response', '')[:200]}...")
            print(f"📚 [SOURCES] {len(result.get('sources', []))} sources found")
            return True
        else:
            print(f"❌ [ERROR] Status: {response.status_code}")
            print(f"📝 [ERROR] {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ [CONNECTION ERROR] {str(e)}")
        return False

def test_vedas_endpoint():
    """Test the vedas endpoint with knowledge base integration."""
    print("\n🧪 [TEST] Testing vedas endpoint with knowledge base...")
    
    url = "http://localhost:8001/ask-vedas"
    payload = {
        "query": "what is karma",
        "user_id": "test_user"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ [SUCCESS] Status: {response.status_code}")
            print(f"📝 [RESPONSE] {result.get('response', '')[:200]}...")
            print(f"📚 [SOURCES] {len(result.get('sources', []))} sources found")
            return True
        else:
            print(f"❌ [ERROR] Status: {response.status_code}")
            print(f"📝 [ERROR] {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ [CONNECTION ERROR] {str(e)}")
        return False

def test_knowledge_agent_direct():
    """Test the knowledge agent directly."""
    print("\n🧪 [TEST] Testing KnowledgeAgent directly...")
    
    try:
        from agents.KnowledgeAgent import KnowledgeAgent
        
        agent = KnowledgeAgent()
        result = agent.query("what is dharma", task_id="test_direct")
        
        print(f"✅ [SUCCESS] KnowledgeAgent working")
        print(f"📝 [RESPONSE] {result.get('response', '')[:200]}...")
        print(f"📚 [SOURCES] {len(result.get('sources', []))} sources found")
        return True
        
    except Exception as e:
        print(f"❌ [ERROR] {str(e)}")
        return False

def main():
    """Run all tests."""
    print("🚀 [KNOWLEDGE BASE INTEGRATION TEST]")
    print("=" * 50)
    
    tests = [
        ("Wellness Endpoint", test_wellness_endpoint),
        ("Vedas Endpoint", test_vedas_endpoint),
        ("KnowledgeAgent Direct", test_knowledge_agent_direct)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🎯 [RUNNING] {test_name}")
        success = test_func()
        results.append((test_name, success))
    
    print("\n" + "=" * 50)
    print("📊 [TEST RESULTS]")
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\n🎯 [SUMMARY] {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 [SUCCESS] All knowledge base integrations working!")
    else:
        print("⚠️  [WARNING] Some integrations need attention")

if __name__ == "__main__":
    main()
