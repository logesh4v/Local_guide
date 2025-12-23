#!/usr/bin/env python3
"""
Test script to verify query validation improvements.
"""
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.query_validator import QueryValidationAgent

def test_queries():
    """Test various queries to see if validation is working properly."""
    validator = QueryValidationAgent()
    
    test_cases = [
        "tell me about madurai",
        "what about dindigul", 
        "describe madurai",
        "food to try now",
        "how to get around",
        "what does enna da mean",
        "is it safe at night",
        "what's the weather like in New York",  # Should be rejected
        "help me with programming",  # Should be rejected
    ]
    
    print("🧪 Testing Query Validation")
    print("=" * 50)
    
    for query in test_cases:
        is_valid = validator.is_supported_topic(query)
        topic = validator.identify_topic(query)
        
        status = "✅ VALID" if is_valid else "❌ REJECTED"
        topic_info = f" (Topic: {topic})" if topic else ""
        
        print(f"{status}: '{query}'{topic_info}")
        
        if not is_valid:
            reason = validator.get_rejection_reason(query)
            print(f"   Reason: {reason}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_queries()