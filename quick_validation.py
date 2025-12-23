"""
Quick validation of key system behaviors based on the question bank.
"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def quick_test():
    """Quick test of key behaviors."""
    print("🚀 QUICK VALIDATION TEST")
    print("=" * 40)
    
    # Test query validation improvements
    from agents.query_validator import QueryValidationAgent
    
    validator = QueryValidationAgent()
    
    # Test cases that should now work better
    test_queries = [
        ("things to try now?", True, "lifestyle"),
        ("what to do?", True, "lifestyle"),
        ("food recommendations", True, "food"),
        ("suggest places in Chennai", False, None),  # Should be rejected
        ("late-night pubs", False, None),  # Should be rejected
        ("What does Sema da mean?", True, "slang"),
        ("Is it safe at night?", True, "safety"),
        ("transport options", True, "transport")
    ]
    
    print("🧪 Testing Query Validation:")
    
    for query, should_pass, expected_topic in test_queries:
        is_valid = validator.validate_query_scope(query)
        topic = validator.identify_topic(query)
        
        status = "✅" if is_valid == should_pass else "❌"
        topic_match = "✅" if topic == expected_topic or expected_topic is None else "❌"
        
        print(f"{status} '{query}' -> Valid: {is_valid}, Topic: {topic} {topic_match}")
    
    print("\n🎯 Key Improvements:")
    print("- 'things to try now?' should be accepted as lifestyle")
    print("- Time-sensitive queries should work better")
    print("- Out-of-scope queries should still be rejected")
    
    # Test RAG retriever
    print("\n🧪 Testing RAG Retriever:")
    from rag_retriever import RAGRetriever
    
    retriever = RAGRetriever()
    time_context = retriever.get_time_context()
    print(f"✅ Time Context: {time_context}")
    
    print("\n🎉 Quick validation complete!")
    print("The system should handle the question bank scenarios well.")

if __name__ == "__main__":
    quick_test()