"""
Test script for RAG functionality.
"""
import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_rag_retriever():
    """Test the RAG retriever functionality."""
    print("🧪 Testing RAG Retriever...")
    
    try:
        from rag_retriever import RAGRetriever
        
        retriever = RAGRetriever()
        
        # Test context loading
        sample_context = """
        # Food & Dining
        ## Traditional Foods
        - **Jigarthanda** - Famous cold drink, best in morning
        - **Idli** - Breakfast item served 7-9 AM
        
        ## Restaurants
        - **Murugan Idli Shop** - Open 6 AM to 10 PM
        """
        
        retriever.load_context_chunks("Madurai", sample_context)
        
        # Test retrieval
        query = "breakfast food"
        chunks = retriever.retrieve_relevant_context(query, "Madurai")
        
        print(f"✅ Retrieved {len(chunks)} chunks for query: '{query}'")
        for chunk in chunks:
            print(f"   - {chunk.section}: {chunk.relevance_score:.2f}")
        
        # Test time context
        time_context = retriever.get_time_context()
        print(f"✅ Time context: {time_context}")
        
        # Test RAG context building
        rag_context = retriever.build_rag_context(query, "Madurai")
        print(f"✅ RAG context built (length: {len(rag_context)} chars)")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG test failed: {str(e)}")
        return False

def test_imports():
    """Test all imports work correctly."""
    print("🧪 Testing imports...")
    
    try:
        from rag_retriever import RAGRetriever
        print("✅ RAG Retriever imported")
        
        from local_guide_system import LocalGuideSystem
        print("✅ Local Guide System imported")
        
        from agents.local_guide_agent import LocalGuideAgent
        print("✅ Local Guide Agent imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {str(e)}")
        return False

def main():
    """Main test function."""
    print("🏛️ Local Guide AI - RAG Testing")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        return
    
    # Test RAG functionality
    if not test_rag_retriever():
        return
    
    print("\n🎉 All tests passed! RAG system is ready.")
    print("\n🚀 To run with your AWS Bearer Token:")
    print("   python setup_and_run.py")

if __name__ == "__main__":
    main()