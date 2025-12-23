#!/usr/bin/env python3
"""
Test script for AgentCore migration validation.
Verifies that the Local Guide AI works correctly with AgentCore wrapper.
"""
import asyncio
import json
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        # Test AgentCore import
        try:
            from bedrock_agentcore import BedrockAgentCoreApp
            print("✅ bedrock-agentcore imported successfully")
        except ImportError:
            print("❌ bedrock-agentcore not found. Run: pip install bedrock-agentcore-starter-toolkit")
            return False
        
        # Test existing system imports
        from local_guide_system import LocalGuideSystem
        from models import Response
        print("✅ Existing system imports successful")
        
        # Test AgentCore main module
        import agentcore_main
        print("✅ AgentCore main module imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

async def test_agentcore_wrapper():
    """Test the AgentCore wrapper functionality."""
    print("\n🧪 Testing AgentCore wrapper...")
    
    try:
        # Import the AgentCore app
        from agentcore_main import app, handle_local_guide_request
        
        # Test basic request
        test_request = {
            "prompt": "What food is Madurai famous for?"
        }
        
        print(f"📤 Sending test request: {test_request}")
        response = await handle_local_guide_request(test_request)
        print(f"📥 Received response: {json.dumps(response, indent=2)}")
        
        # Validate response structure
        required_fields = ["response", "is_refusal", "city", "status"]
        for field in required_fields:
            if field not in response:
                print(f"❌ Missing required field: {field}")
                return False
        
        print("✅ AgentCore wrapper test successful")
        return True
        
    except Exception as e:
        print(f"❌ AgentCore wrapper test failed: {e}")
        return False

async def test_city_selection():
    """Test city selection functionality."""
    print("\n🧪 Testing city selection...")
    
    try:
        from agentcore_main import handle_local_guide_request
        
        # Test Madurai selection
        madurai_request = {
            "prompt": "Tell me about local food",
            "city": "Madurai"
        }
        
        response = await handle_local_guide_request(madurai_request)
        print(f"📍 Madurai response: {response.get('city')} - {response.get('status')}")
        
        # Test Dindigul selection
        dindigul_request = {
            "prompt": "Tell me about biryani",
            "city": "Dindigul"
        }
        
        response = await handle_local_guide_request(dindigul_request)
        print(f"📍 Dindigul response: {response.get('city')} - {response.get('status')}")
        
        # Test invalid city
        invalid_request = {
            "prompt": "Tell me about food",
            "city": "Chennai"
        }
        
        response = await handle_local_guide_request(invalid_request)
        if response.get('is_refusal'):
            print("✅ Invalid city correctly refused")
        else:
            print("❌ Invalid city should be refused")
            return False
        
        print("✅ City selection test successful")
        return True
        
    except Exception as e:
        print(f"❌ City selection test failed: {e}")
        return False

async def test_refusal_behavior():
    """Test refusal behavior for out-of-scope queries."""
    print("\n🧪 Testing refusal behavior...")
    
    try:
        from agentcore_main import handle_local_guide_request
        
        # Test out-of-scope query
        out_of_scope_request = {
            "prompt": "What's the weather like in New York?"
        }
        
        response = await handle_local_guide_request(out_of_scope_request)
        
        if response.get('is_refusal'):
            print("✅ Out-of-scope query correctly refused")
            print(f"📝 Refusal reason: {response.get('refusal_reason')}")
        else:
            print("❌ Out-of-scope query should be refused")
            return False
        
        # Test empty query
        empty_request = {
            "prompt": ""
        }
        
        response = await handle_local_guide_request(empty_request)
        
        if response.get('is_refusal'):
            print("✅ Empty query correctly refused")
        else:
            print("❌ Empty query should be refused")
            return False
        
        print("✅ Refusal behavior test successful")
        return True
        
    except Exception as e:
        print(f"❌ Refusal behavior test failed: {e}")
        return False

async def test_health_check():
    """Test health check functionality."""
    print("\n🧪 Testing health check...")
    
    try:
        from agentcore_main import health_check
        
        health_response = await health_check()
        print(f"🏥 Health check response: {json.dumps(health_response, indent=2)}")
        
        if health_response.get('status') in ['healthy', 'unhealthy']:
            print("✅ Health check test successful")
            return True
        else:
            print("❌ Health check returned invalid status")
            return False
        
    except Exception as e:
        print(f"❌ Health check test failed: {e}")
        return False

def test_configuration_files():
    """Test that configuration files exist and are valid."""
    print("\n🧪 Testing configuration files...")
    
    # Check AgentCore config
    config_file = ".bedrock_agentcore.yaml"
    if os.path.exists(config_file):
        print(f"✅ {config_file} exists")
    else:
        print(f"❌ {config_file} missing")
        return False
    
    # Check context files
    context_files = [
        "context/madurai_context.md",
        "context/dindigul_context.md"
    ]
    
    for file_path in context_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            return False
    
    # Check system prompt
    system_prompt = ".kiro/system_prompt.txt"
    if os.path.exists(system_prompt):
        print(f"✅ {system_prompt} exists")
    else:
        print(f"❌ {system_prompt} missing")
        return False
    
    print("✅ Configuration files test successful")
    return True

async def run_all_tests():
    """Run all migration validation tests."""
    print("🏛️ Local Guide AI - AgentCore Migration Test Suite")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("Configuration Files", test_configuration_files),
        ("AgentCore Wrapper", test_agentcore_wrapper),
        ("City Selection", test_city_selection),
        ("Refusal Behavior", test_refusal_behavior),
        ("Health Check", test_health_check),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! AgentCore migration is ready.")
        print("\n🚀 Next steps:")
        print("1. agentcore dev                    # Start development server")
        print("2. agentcore invoke --dev '{...}'   # Test locally")
        print("3. agentcore launch                 # Deploy to AWS")
    else:
        print(f"\n⚠️ {total - passed} tests failed. Please fix issues before deployment.")
        return False
    
    return passed == total

if __name__ == "__main__":
    # Run the test suite
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)