"""
Test the improved query validation.
"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_queries():
    """Test various queries."""
    from agents.query_validator import QueryValidationAgent
    
    validator = QueryValidationAgent()
    
    test_queries = [
        "things to try now?",
        "what to do now?",
        "activities for today",
        "what can I see?",
        "recommend something",
        "suggest places to visit",
        "tell me about madurai",  # Should still be rejected (too broad)
        "food recommendations",
        "transport options"
    ]
    
    print("🧪 Testing Query Validation:")
    print("=" * 40)
    
    for query in test_queries:
        is_valid = validator.validate_query_scope(query)
        topic = validator.identify_topic(query)
        status = "✅ ACCEPTED" if is_valid else "🚫 REJECTED"
        
        print(f"{status} '{query}' -> Topic: {topic}")
    
    print("\n🎯 The query 'things to try now?' should now be ACCEPTED!")

if __name__ == "__main__":
    test_queries()