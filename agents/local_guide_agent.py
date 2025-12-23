"""
Local Guide Agent for Local Guide AI.
Primary agent using Amazon Nova Premier via Bedrock for response generation with RAG.
"""
import os
import sys
from typing import Optional
from strands import Agent
from strands.models import BedrockModel
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Response, CityContext
from rag_retriever import RAGRetriever


class LocalGuideAgent:
    """Primary agent for generating local guide responses using Amazon Nova Premier."""
    
    def __init__(self):
        """Initialize the Local Guide Agent with Nova Premier model and RAG."""
        self.model = self._configure_model()
        self.agent = self._create_agent()
        self.system_prompt_template = self._load_system_prompt()
        self.rag_retriever = RAGRetriever()
    
    def _configure_model(self) -> BedrockModel:
        """
        Configure Amazon Bedrock model with Nova Premier.
        
        Returns:
            Configured BedrockModel instance
        """
        # Check for Bearer Token first, then fallback to other credentials
        bearer_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
        if bearer_token:
            # Use bearer token authentication
            return BedrockModel(
                model_id="us.amazon.nova-premier-v1:0",
                region_name="us-east-1",
                temperature=0.1,
                max_tokens=2048,
                client_args={"bearer_token": bearer_token}
            )
        else:
            # Fallback to regular credentials
            return BedrockModel(
                model_id="us.amazon.nova-premier-v1:0",
                region_name=os.getenv("AWS_REGION", "us-east-1"),
                temperature=0.1,
                max_tokens=2048,
            )
    
    def _load_system_prompt(self) -> str:
        """
        Load system prompt from file.
        
        Returns:
            System prompt template string
        """
        try:
            prompt_path = os.path.join(".kiro", "system_prompt.txt")
            if os.path.exists(prompt_path):
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                # Fallback system prompt if file not found
                return self._get_fallback_system_prompt()
        except Exception:
            return self._get_fallback_system_prompt()
    
    def _get_fallback_system_prompt(self) -> str:
        """
        Get fallback system prompt if file loading fails.
        
        Returns:
            Fallback system prompt string
        """
        return """You are a Local Guide AI for Tamil Nadu cities. You must follow these STRICT rules:

CONTEXT SUPREMACY:
- You can ONLY use information from the loaded city context file
- You must NEVER use general world knowledge or external information
- If information is not in the context file, you MUST refuse to answer

REFUSAL RESPONSES:
When you cannot find information in the context, use ONLY one of these exact phrases:
- "This isn't covered in my local context."
- "I don't have enough local data to answer that."
- "My knowledge is limited to what's in the context file."

RESPONSE STYLE:
- Use a local, practical tone
- Include Tamil-English mix where the context supports it
- Avoid tourism-style or generic phrasing
- Be direct and helpful when you have the information

Remember: Your role is to provide accurate local guidance based solely on the authoritative context provided for the selected city."""
    
    def _create_agent(self) -> Agent:
        """
        Create Strands agent with configured model.
        
        Returns:
            Configured Agent instance
        """
        return Agent(
            model=self.model,
            tools=[],  # No tools needed for this agent
        )
    
    def apply_system_prompt(self, context: str) -> str:
        """
        Apply system prompt with city context.
        
        Args:
            context: City-specific context content
            
        Returns:
            Complete system prompt with context
        """
        context_section = f"\n\nCITY CONTEXT:\n{context}\n\nRemember: Use ONLY the information provided in the CITY CONTEXT above. Do not use any external knowledge."
        return self.system_prompt_template + context_section
    
    def generate_response(self, query: str, context: str, city: str = "") -> str:
        """
        Generate response using Nova Premier with RAG-enhanced context.
        
        Args:
            query: User query text
            context: City-specific context content
            city: City name for RAG retrieval
            
        Returns:
            Generated response text
        """
        if not query or not query.strip():
            return "This isn't covered in my local context."
        
        if not context or not context.strip():
            return "I don't have enough local data to answer that."
        
        try:
            # Load context into RAG retriever if not already loaded
            if city and city.lower() not in self.rag_retriever.context_chunks:
                self.rag_retriever.load_context_chunks(city, context)
            
            # Get RAG-enhanced context
            if city:
                rag_context = self.rag_retriever.build_rag_context(query, city)
                enhanced_context = f"{rag_context}\n\nFULL CONTEXT:\n{context}"
            else:
                enhanced_context = context
            
            # Apply system prompt with enhanced context
            full_system_prompt = self.apply_system_prompt(enhanced_context)
            
            # Create a new agent instance with the context-specific system prompt
            context_agent = Agent(
                model=self.model,
                system_prompt=full_system_prompt,
                tools=[]
            )
            
            # Generate response
            response = context_agent(query)
            
            # Ensure response is a string
            if hasattr(response, 'text'):
                return response.text
            elif isinstance(response, str):
                return response
            else:
                return str(response)
                
        except Exception as e:
            # Log error and return refusal
            print(f"Error generating response: {str(e)}")
            return "My knowledge is limited to what's in the context file."
    
    def create_response_object(self, query: str, context: str, city: str) -> Response:
        """
        Create a Response object with generated content using RAG.
        
        Args:
            query: User query text
            context: City-specific context content
            city: Selected city name
            
        Returns:
            Response object with generated content
        """
        response_text = self.generate_response(query, context, city)
        
        # Check if response is a refusal
        refusal_phrases = [
            "This isn't covered in my local context.",
            "I don't have enough local data to answer that.",
            "My knowledge is limited to what's in the context file."
        ]
        
        is_refusal = any(phrase in response_text for phrase in refusal_phrases)
        refusal_reason = "Information not available in context" if is_refusal else None
        
        return Response(
            text=response_text,
            is_refusal=is_refusal,
            refusal_reason=refusal_reason,
            source_context=f"{city} context (RAG-enhanced)",
            validation_passed=True  # Will be validated by Guard Agent
        )
    
    def validate_response_against_context(self, response_text: str, context: str) -> bool:
        """
        Basic validation that response content exists in context.
        
        Args:
            response_text: Generated response text
            context: Source context content
            
        Returns:
            True if response appears to be based on context, False otherwise
        """
        if not response_text or not context:
            return False
        
        # Check for refusal responses (these are always valid)
        refusal_phrases = [
            "This isn't covered in my local context.",
            "I don't have enough local data to answer that.",
            "My knowledge is limited to what's in the context file."
        ]
        
        if any(phrase in response_text for phrase in refusal_phrases):
            return True
        
        # Basic check: response should contain some words that appear in context
        response_words = set(response_text.lower().split())
        context_words = set(context.lower().split())
        
        # Remove common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
        
        response_content_words = response_words - common_words
        context_content_words = context_words - common_words
        
        if not response_content_words:
            return False
        
        # Check if at least 30% of content words in response appear in context
        overlap = response_content_words.intersection(context_content_words)
        overlap_ratio = len(overlap) / len(response_content_words)
        
        return overlap_ratio >= 0.3
    
    def get_model_info(self) -> dict:
        """
        Get information about the configured model.
        
        Returns:
            Dictionary with model configuration details
        """
        try:
            # Try to get model_id from different possible attributes
            model_id = getattr(self.model, 'model_id', None) or \
                      getattr(self.model, 'model_name', None) or \
                      getattr(self.model, 'id', None) or \
                      "us.amazon.nova-premier-v1:0"
            
            region = getattr(self.model, 'region_name', None) or \
                    getattr(self.model, 'region', None) or \
                    "us-east-1"
            
            temperature = getattr(self.model, 'temperature', 0.1)
            max_tokens = getattr(self.model, 'max_tokens', 2048)
            
            return {
                "model_id": model_id,
                "region": region,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "provider": "Amazon Bedrock"
            }
        except Exception as e:
            # Fallback if there are any issues
            return {
                "model_id": "us.amazon.nova-premier-v1:0",
                "region": "us-east-1",
                "temperature": 0.1,
                "max_tokens": 2048,
                "provider": "Amazon Bedrock"
            }
    
    def test_model_connection(self) -> bool:
        """
        Test if the model connection is working.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            test_response = self.generate_response(
                "test", 
                "This is a test context for connection validation.",
                "test"
            )
            return bool(test_response and test_response.strip())
        except Exception as e:
            print(f"Model connection test failed: {str(e)}")
            return False