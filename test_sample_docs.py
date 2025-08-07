#!/usr/bin/env python3
"""
Test the knowledge base with sample documents
"""

import os
from pathlib import Path
from bhiv_knowledge_base import BHIVKnowledgeBase
from dotenv import load_dotenv

def create_sample_documents():
    """Create some sample documents for testing"""
    
    sample_docs = {
        "vedic_knowledge.txt": """
        The Vedas are ancient Sanskrit texts that form the foundation of Hindu philosophy and spirituality.
        They contain hymns, prayers, and rituals that have been preserved for thousands of years.
        
        The four main Vedas are:
        1. Rigveda - Collection of hymns and prayers
        2. Samaveda - Musical chants and melodies
        3. Yajurveda - Ritual formulas and procedures
        4. Atharvaveda - Spells, charms, and everyday wisdom
        
        These texts represent the earliest form of Indian literature and contain profound
        philosophical insights about the nature of reality, consciousness, and the divine.
        """,
        
        "ayurveda_basics.txt": """
        Ayurveda is the traditional system of medicine from India, dating back over 5000 years.
        It focuses on maintaining health through balance of mind, body, and spirit.
        
        Key principles of Ayurveda:
        - Three doshas: Vata (air/space), Pitta (fire/water), Kapha (earth/water)
        - Prevention is better than cure
        - Treatment of root causes, not just symptoms
        - Individualized medicine based on constitution
        
        Ayurvedic treatments include:
        - Herbal medicines
        - Dietary recommendations
        - Lifestyle modifications
        - Yoga and meditation
        - Panchakarma (detoxification)
        """,
        
        "yoga_philosophy.txt": """
        Yoga is a comprehensive system for physical, mental, and spiritual development.
        The word "yoga" means "union" - the joining of individual consciousness with universal consciousness.
        
        The Eight Limbs of Yoga (Ashtanga):
        1. Yama - Ethical restraints
        2. Niyama - Observances
        3. Asana - Physical postures
        4. Pranayama - Breath control
        5. Pratyahara - Withdrawal of senses
        6. Dharana - Concentration
        7. Dhyana - Meditation
        8. Samadhi - Union/enlightenment
        
        Yoga philosophy teaches that suffering comes from ignorance of our true nature,
        and through practice, we can achieve liberation and lasting peace.
        """
    }
    
    # Create sample documents directory
    sample_dir = Path("sample_documents")
    sample_dir.mkdir(exist_ok=True)
    
    created_files = []
    for filename, content in sample_docs.items():
        file_path = sample_dir / filename
        file_path.write_text(content.strip(), encoding='utf-8')
        created_files.append(str(file_path))
        print(f"✅ Created sample document: {filename}")
    
    return created_files

def test_knowledge_base():
    """Test the knowledge base with sample documents"""
    
    # Load configuration
    load_dotenv()
    nas_path = os.getenv("NAS_PATH", r"\\192.168.0.94\Guruukul_DB")
    
    # Initialize knowledge base
    print("🚀 Initializing BHIV Knowledge Base...")
    kb = BHIVKnowledgeBase(nas_path, use_qdrant=False)  # Disable Qdrant for now
    
    # Test system
    test_results = kb.test_system()
    print("\n🧪 System Test Results:")
    for component, status in test_results.items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {component}: {'OK' if status else 'FAILED'}")
    
    if not test_results.get("nas_connection", False):
        print("❌ NAS connection failed. Cannot proceed with testing.")
        return
    
    # Create sample documents
    print("\n📝 Creating sample documents...")
    sample_files = create_sample_documents()
    
    # Add documents to knowledge base
    print("\n📚 Adding documents to knowledge base...")
    document_ids = []
    for file_path in sample_files:
        try:
            doc_id = kb.add_document(file_path)
            document_ids.append(doc_id)
            print(f"✅ Added: {Path(file_path).name} -> {doc_id}")
        except Exception as e:
            print(f"❌ Failed to add {file_path}: {e}")
    
    # List documents
    print("\n📋 Documents in knowledge base:")
    documents = kb.list_documents()
    for doc in documents:
        print(f"  - {doc['document_id']}: {doc['original_filename']} ({doc['file_size']} bytes)")
    
    # Test search functionality
    print("\n🔍 Testing search functionality...")
    search_queries = [
        "Vedas",
        "Ayurveda medicine",
        "yoga philosophy",
        "doshas",
        "meditation"
    ]
    
    for query in search_queries:
        print(f"\n🔎 Searching for: '{query}'")
        results = kb.search(query, limit=3)
        if results:
            for i, result in enumerate(results, 1):
                print(f"  {i}. Document: {result['document_id']}")
                print(f"     Content: {result['content'][:100]}...")
                print(f"     Score: {result['score']}")
        else:
            print("  No results found")
    
    # Test document content retrieval
    if document_ids:
        print(f"\n📖 Testing document content retrieval...")
        doc_id = document_ids[0]
        content = kb.get_document_content(doc_id)
        if content:
            print(f"✅ Retrieved content for {doc_id}:")
            print(f"   {content[:200]}...")
        else:
            print(f"❌ Failed to retrieve content for {doc_id}")
    
    # Show final stats
    print("\n📊 Final Knowledge Base Stats:")
    stats = kb.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n🎉 Knowledge base testing completed!")
    print(f"✅ Successfully added {len(document_ids)} documents to the NAS-based knowledge base")
    print(f"📍 Knowledge base location: {stats.get('knowledge_base_path', 'Unknown')}")

if __name__ == "__main__":
    test_knowledge_base()
