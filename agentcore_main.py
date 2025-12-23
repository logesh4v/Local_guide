"""
AgentCore wrapper for Local Guide AI system.
Migrates from Strands Agents to Bedrock AgentCore runtime.
"""
import os
import sys
from typing import Dict, Any

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from bedrock_agentcore import BedrockAgentCoreApp
except ImportError:
    print("❌ bedrock-agentcore not installed. Run: pip install bedrock-agentcore-starter-toolkit")
    sys.exit(1)

from local_guide_system import LocalGuideSystem
from models import Response

# Initialize AgentCore app
app = BedrockAgentCoreApp()

# Initialize the existing Local Guide system
guide_system = None

def initialize_system():
    """Initialize the Local Guide system once."""
    global guide_system
    if guide_system is None:
        guide_system = LocalGuideSystem()
        guide_system.initialize()
        print("✅ Local Guide system initialized for AgentCore")

@app.entrypoint
async def handle_local_guide_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    AgentCore entrypoint for Local Guide AI.
    
    Handles requests in AgentCore format and returns structured responses.
    Maintains compatibility with existing Strands-based system.
    
    Args:
        request: AgentCore request format
                Expected: {"prompt": "user question", "city": "optional city"}
    
    Returns:
        Dict with response, metadata, and system status
    """
    try:
        # Initialize system if not already done
        initialize_system()
        
        # Extract request data
        prompt = request.get("prompt", "").strip()
        requested_city = request.get("city", None)
        
        # Validate input
        if not prompt:
            return {
                "response": "Please provide a question about Madurai or Dindigul.",
                "is_refusal": True,
                "refusal_reason": "Empty query",
                "city": None,
                "status": "error"
            }
        
        # Handle city selection if provided
        if requested_city:
            success, message = guide_system.select_city(requested_city)
            if not success:
                return {
                    "response": f"Sorry, I can only help with Madurai and Dindigul. {message}",
                    "is_refusal": True,
                    "refusal_reason": "Unsupported city",
                    "city": None,
                    "status": "error"
                }
        
        # Process the query using existing system
        response = guide_system.process_query(prompt)
        
        # Get current system status
        status = guide_system.get_system_status()
        
        # Return structured response for AgentCore
        return {
            "response": response.text,
            "is_refusal": response.is_refusal,
            "refusal_reason": response.refusal_reason if response.is_refusal else None,
            "city": status.get('selected_city'),
            "model_info": status.get('model_info'),
            "status": "success",
            "conversation_length": status.get('conversation_length', 0),
            "timestamp": str(response.timestamp) if hasattr(response, 'timestamp') else None
        }
        
    except Exception as e:
        # Handle any system errors gracefully
        error_message = "I don't have enough local data to answer that."
        
        return {
            "response": error_message,
            "is_refusal": True,
            "refusal_reason": "System error",
            "city": None,
            "status": "error",
            "error_details": str(e) if os.getenv("DEBUG_MODE") else None
        }

@app.health_check
async def health_check() -> Dict[str, Any]:
    """
    AgentCore health check endpoint.
    
    Returns system health status for monitoring.
    """
    try:
        initialize_system()
        
        # Run system health validation
        health = guide_system.validate_system_health()
        
        return {
            "status": "healthy" if health['overall_status'] == 'healthy' else "unhealthy",
            "components": health.get('components', {}),
            "issues": health.get('issues', []),
            "cities_available": guide_system.get_available_cities(),
            "model_connected": health.get('components', {}).get('local_guide') == 'healthy'
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "components": {},
            "issues": ["System initialization failed"]
        }

# Additional AgentCore configuration
app.config.update({
    "name": "Local Guide AI",
    "description": "Context-driven AI assistant for Tamil Nadu cities (Madurai and Dindigul)",
    "version": "2.0.0-agentcore",
    "author": "Kiro Heroes Challenge Week 5",
    "supported_cities": ["Madurai", "Dindigul"],
    "supported_topics": ["food", "transport", "language", "safety", "lifestyle"]
})

if __name__ == "__main__":
    # For local development testing
    print("🏛️ Local Guide AI - AgentCore Version")
    print("Run with: agentcore dev")
    print("Test with: agentcore invoke --dev '{\"prompt\": \"What food is Madurai famous for?\"}'")