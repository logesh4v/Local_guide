"""
Setup script to configure AWS Bearer Token and run the Local Guide AI.
"""
import os
import sys

def setup_environment():
    """Set up environment variables."""
    # Check if bearer token is already set in environment
    bearer_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
    
    if not bearer_token:
        print("❌ AWS_BEARER_TOKEN_BEDROCK not found in environment variables")
        print("Please set your AWS credentials using one of these methods:")
        print("1. export AWS_BEARER_TOKEN_BEDROCK=your_token")
        print("2. export AWS_ACCESS_KEY_ID=your_key")
        print("3. export AWS_SECRET_ACCESS_KEY=your_secret")
        return False
    else:
        print("✅ AWS Bearer Token found in environment")
    
    # Set region if not already set
    if not os.getenv("AWS_REGION"):
        os.environ["AWS_REGION"] = "us-east-1"
        print("✅ AWS Region set to us-east-1")
    else:
        print(f"✅ AWS Region: {os.getenv('AWS_REGION')}")
    
    return True

def test_system():
    """Test the system with RAG."""
    print("\n🧪 Testing RAG-enhanced Local Guide AI...")
    
    try:
        from local_guide_system import LocalGuideSystem
        
        system = LocalGuideSystem()
        system.initialize()
        
        # Test city selection
        success, message = system.select_city("Madurai")
        if success:
            print(f"✅ {message}")
            
            # Test RAG query
            response = system.process_query("What food is good for breakfast right now?")
            print(f"\n🤖 Response: {response.text}")
            print(f"📊 Source: {response.source_context}")
            
        else:
            print(f"❌ {message}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

def main():
    """Main function."""
    print("🏛️ Local Guide AI - RAG Setup")
    print("=" * 50)
    
    # Setup environment
    setup_environment()
    
    # Test system
    test_system()
    
    print("\n🚀 Setup complete! You can now run:")
    print("   python cli_app.py")
    print("   streamlit run app.py")

if __name__ == "__main__":
    main()