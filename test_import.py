"""Quick test to verify imports work correctly."""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from local_guide_system import LocalGuideSystem
    print("✅ LocalGuideSystem imported successfully")
    
    from models import Query, Response, AppState, CityContext
    print("✅ Models imported successfully")
    
    from agents.context_loader import ContextLoaderAgent
    print("✅ ContextLoaderAgent imported successfully")
    
    from agents.query_validator import QueryValidationAgent
    print("✅ QueryValidationAgent imported successfully")
    
    from agents.guard_agent import GuardAgent
    print("✅ GuardAgent imported successfully")
    
    from refusal_handler import RefusalHandler
    print("✅ RefusalHandler imported successfully")
    
    print("\n🎉 All imports successful! System is ready.")
    
except Exception as e:
    print(f"❌ Import error: {str(e)}")
    import traceback
    traceback.print_exc()
