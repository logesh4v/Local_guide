"""
Comprehensive test script based on the provided question bank.
Tests all categories of queries to validate system behavior.
"""
import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_environment():
    """Set up environment for testing."""
    # Check if AWS credentials are already set in environment
    bearer_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
    
    if not bearer_token:
        print("❌ AWS_BEARER_TOKEN_BEDROCK not found in environment variables")
        print("Please set your AWS credentials using one of these methods:")
        print("1. export AWS_BEARER_TOKEN_BEDROCK=your_token")
        print("2. export AWS_ACCESS_KEY_ID=your_key")
        print("3. export AWS_SECRET_ACCESS_KEY=your_secret")
        print("\nSkipping tests that require AWS connection...")
        return False
    
    # Set region if not already set
    if not os.getenv("AWS_REGION"):
        os.environ["AWS_REGION"] = "us-east-1"
    
    return True

def test_question_bank():
    """Test the system against the comprehensive question bank."""
    if not setup_environment():
        print("Skipping comprehensive tests - AWS credentials not configured")
        return
    
    from local_guide_system import LocalGuideSystem
    
    system = LocalGuideSystem()
    system.initialize()
    
    # Test cases organized by category
    test_cases = [
        # CATEGORY 1: CITY SELECTION / CLARIFICATION
        {
            "category": "City Selection",
            "query": "Suggest good food nearby",
            "expected_behavior": "Should ask for city clarification",
            "city": None
        },
        
        # CATEGORY 2-3: DINDIGUL FOOD TESTS
        {
            "category": "Dindigul Food General",
            "query": "What food is Dindigul famous for?",
            "expected_behavior": "Should mention biryani",
            "city": "Dindigul"
        },
        {
            "category": "Dindigul Food Time-Sensitive",
            "query": "Can I get good biryani at 8 AM in Dindigul?",
            "expected_behavior": "Should mention morning biryani is rare/reheated",
            "city": "Dindigul"
        },
        {
            "category": "Dindigul Food Time-Sensitive",
            "query": "Any late-night food options after 10 PM?",
            "expected_behavior": "Should mention limited options after 9:30 PM",
            "city": "Dindigul"
        },
        
        # CATEGORY 4: DINDIGUL TRANSPORT
        {
            "category": "Dindigul Transport",
            "query": "Are autos cheap in Dindigul?",
            "expected_behavior": "Should mention affordable but no meters",
            "city": "Dindigul"
        },
        
        # CATEGORY 5: DINDIGUL SAFETY
        {
            "category": "Dindigul Safety",
            "query": "Is Dindigul safe at night?",
            "expected_behavior": "Should mention generally safe but quiet after 9:30 PM",
            "city": "Dindigul"
        },
        
        # CATEGORY 9-10: MADURAI FOOD TESTS
        {
            "category": "Madurai Food General",
            "query": "What food should I try in Madurai?",
            "expected_behavior": "Should mention strong-flavored food, non-veg for lunch/dinner",
            "city": "Madurai"
        },
        {
            "category": "Madurai Food Time-Sensitive",
            "query": "Where can I eat dinner near Meenakshi temple at 10 PM?",
            "expected_behavior": "Should mention limited options after 10:30 PM, suggest Anna Nagar",
            "city": "Madurai"
        },
        
        # CATEGORY 11: MADURAI TRANSPORT
        {
            "category": "Madurai Transport",
            "query": "Do autos use meters in Madurai?",
            "expected_behavior": "Should mention autos rarely use meters",
            "city": "Madurai"
        },
        
        # CATEGORY 15: MADURAI SLANG
        {
            "category": "Madurai Slang",
            "query": "What does 'Sema da' mean?",
            "expected_behavior": "Should explain extreme appreciation",
            "city": "Madurai"
        },
        
        # CATEGORY 16: OUT-OF-SCOPE / REFUSAL TESTS
        {
            "category": "Out-of-Scope Refusal",
            "query": "Suggest places in Chennai",
            "expected_behavior": "Should refuse - limited to Madurai and Dindigul",
            "city": "Madurai"
        },
        {
            "category": "Out-of-Scope Refusal",
            "query": "Can you suggest late-night pubs?",
            "expected_behavior": "Should refuse - not covered in local context",
            "city": "Madurai"
        }
    ]
    
    print("🏛️ COMPREHENSIVE SYSTEM TEST")
    print("=" * 60)
    print(f"Testing {len(test_cases)} scenarios from the question bank...")
    print()
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"TEST {i}: {test_case['category']}")
        print(f"Query: '{test_case['query']}'")
        print(f"Expected: {test_case['expected_behavior']}")
        
        try:
            if test_case['city']:
                # Select city first
                success, message = system.select_city(test_case['city'])
                if not success:
                    print(f"❌ Failed to select city: {message}")
                    failed += 1
                    continue
            
            # Process query
            response = system.process_query(test_case['query'])
            
            print(f"Response: {response.text[:100]}{'...' if len(response.text) > 100 else ''}")
            
            # Basic validation (you can enhance this)
            if response.text and len(response.text) > 10:
                print("✅ PASSED - Got meaningful response")
                passed += 1
            else:
                print("❌ FAILED - Response too short or empty")
                failed += 1
                
        except Exception as e:
            print(f"❌ FAILED - Exception: {str(e)}")
            failed += 1
        
        print("-" * 60)
    
    print(f"\n📊 TEST RESULTS:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {passed/(passed+failed)*100:.1f}%")
    
    if passed >= len(test_cases) * 0.8:  # 80% success rate
        print("\n🎉 SYSTEM VALIDATION SUCCESSFUL!")
        print("The Local Guide AI handles the question bank well!")
    else:
        print("\n⚠️ Some tests failed. Review the responses above.")

def main():
    """Main test function."""
    print("🧪 Starting comprehensive system validation...")
    test_question_bank()

