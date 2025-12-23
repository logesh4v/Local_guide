"""
Property-based tests for context-only response generation.
**Feature: local-guide-ai, Property 3: Context-only response generation**
**Validates: Requirements 2.3**
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.local_guide_agent import LocalGuideAgent
from models import Response


class TestContextOnlyResponsesProperty:
    """Property-based tests for context-only response generation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Note: This will require AWS credentials to be configured
        # For testing without AWS, we'll mock the responses
        self.agent = LocalGuideAgent()
        
        # Sample contexts for testing
        self.sample_contexts = {
            'madurai': """# Madurai Context
            Famous for Meenakshi Temple and Jigarthanda.
            Traditional food includes idli, dosa, and biryani.
            Local transport includes buses and auto rickshaws.
            """,
            'dindigul': """# Dindigul Context
            Famous for Thalappakatti Biryani and lock manufacturing.
            Known as Lock City of Tamil Nadu.
            Local specialties include mutton biryani and vada curry.
            """
        }
    
    @given(st.sampled_from([
        "What food is famous here?",
        "Tell me about local transport",
        "What are the specialties?",
        "How do people travel?",
        "What is this place known for?"
    ]))
    @settings(max_examples=20)  # Reduced for API calls
    def test_context_only_response_property(self, query: str):
        """
        **Feature: local-guide-ai, Property 3: Context-only response generation**
        For any valid query, the Local Guide Agent should generate responses using 
        only information present in the loaded context file content.
        """
        # Test with Madurai context
        madurai_context = self.sample_contexts['madurai']
        
        try:
            response_text = self.agent.generate_response(query, madurai_context)
            
            # Response should not be empty
            assert response_text and response_text.strip(), f"Response should not be empty for query: {query}"
            
            # Response should either be a refusal or contain context-based information
            is_refusal = any(phrase in response_text for phrase in [
                "This isn't covered in my local context.",
                "I don't have enough local data to answer that.",
                "My knowledge is limited to what's in the context file."
            ])
            
            if not is_refusal:
                # If not a refusal, response should be based on context
                assert self.agent.validate_response_against_context(response_text, madurai_context), \
                    f"Response should be based on context for query: {query}"
                
                # Response should not contain information from other cities
                assert 'thalappakatti' not in response_text.lower(), \
                    f"Response should not contain Dindigul-specific info for Madurai query: {query}"
        
        except Exception as e:
            # If there's an API error, the agent should return a refusal
            if "AWS" in str(e) or "credentials" in str(e) or "connection" in str(e):
                pytest.skip(f"AWS connection not available for testing: {e}")
            else:
                raise e
    
    @given(st.sampled_from(['madurai', 'dindigul']))
    @settings(max_examples=10)
    def test_context_isolation_property(self, city: str):
        """
        Test that responses are isolated to the selected city's context.
        """
        context = self.sample_contexts[city]
        other_city = 'dindigul' if city == 'madurai' else 'madurai'
        
        query = "What is this place famous for?"
        
        try:
            response_text = self.agent.generate_response(query, context)
            
            if response_text and not any(phrase in response_text for phrase in [
                "This isn't covered in my local context.",
                "I don't have enough local data to answer that.",
                "My knowledge is limited to what's in the context file."
            ]):
                # Response should contain city-specific information
                assert city in response_text.lower() or any(
                    keyword in response_text.lower() 
                    for keyword in self._get_city_keywords(city)
                ), f"Response should contain {city}-specific information"
                
                # Response should not contain other city's specific information
                other_keywords = self._get_city_keywords(other_city)
                assert not any(
                    keyword in response_text.lower() 
                    for keyword in other_keywords
                ), f"Response should not contain {other_city}-specific information"
        
        except Exception as e:
            if "AWS" in str(e) or "credentials" in str(e):
                pytest.skip(f"AWS connection not available for testing: {e}")
            else:
                raise e
    
    def _get_city_keywords(self, city: str) -> list:
        """Get city-specific keywords for validation."""
        keywords = {
            'madurai': ['meenakshi', 'jigarthanda'],
            'dindigul': ['thalappakatti', 'lock city']
        }
        return keywords.get(city, [])
    
    @given(st.text(min_size=1, max_size=50))
    @settings(max_examples=10)
    def test_empty_context_handling(self, query: str):
        """
        Test handling of queries with empty or invalid context.
        """
        assume(query.strip())  # Skip empty queries
        
        # Test with empty context
        response = self.agent.generate_response(query, "")
        assert response in [
            "This isn't covered in my local context.",
            "I don't have enough local data to answer that.",
            "My knowledge is limited to what's in the context file."
        ], "Should return standardized refusal for empty context"
        
        # Test with None context
        response = self.agent.generate_response(query, None)
        assert response in [
            "This isn't covered in my local context.",
            "I don't have enough local data to answer that.",
            "My knowledge is limited to what's in the context file."
        ], "Should return standardized refusal for None context"
    
    def test_response_object_creation(self):
        """
        Test creation of Response objects with proper metadata.
        """
        query = "What food is famous here?"
        context = self.sample_contexts['madurai']
        city = "Madurai"
        
        try:
            response_obj = self.agent.create_response_object(query, context, city)
            
            assert isinstance(response_obj, Response)
            assert response_obj.text
            assert response_obj.source_context == "Madurai context"
            assert response_obj.validation_passed is True
            
            # Check refusal detection
            if response_obj.is_refusal:
                assert response_obj.refusal_reason is not None
                assert response_obj.is_standardized_refusal()
            else:
                assert response_obj.refusal_reason is None
        
        except Exception as e:
            if "AWS" in str(e) or "credentials" in str(e):
                pytest.skip(f"AWS connection not available for testing: {e}")
            else:
                raise e
    
    def test_system_prompt_application(self):
        """
        Test that system prompt is properly applied with context.
        """
        context = self.sample_contexts['madurai']
        system_prompt = self.agent.apply_system_prompt(context)
        
        # System prompt should contain the original template
        assert "CONTEXT SUPREMACY" in system_prompt
        assert "REFUSAL RESPONSES" in system_prompt
        
        # System prompt should contain the provided context
        assert "Meenakshi Temple" in system_prompt
        assert "CITY CONTEXT:" in system_prompt
    
    def test_response_validation_against_context(self):
        """
        Test validation of responses against context.
        """
        context = self.sample_contexts['madurai']
        
        # Valid response (contains context words)
        valid_response = "Madurai is famous for Meenakshi Temple and Jigarthanda."
        assert self.agent.validate_response_against_context(valid_response, context)
        
        # Invalid response (no context words)
        invalid_response = "This city has many shopping malls and modern buildings."
        assert not self.agent.validate_response_against_context(invalid_response, context)
        
        # Refusal response (always valid)
        refusal_response = "This isn't covered in my local context."
        assert self.agent.validate_response_against_context(refusal_response, context)
        
        # Empty response (invalid)
        assert not self.agent.validate_response_against_context("", context)
        assert not self.agent.validate_response_against_context(None, context)
    
    def test_model_configuration(self):
        """
        Test that model is properly configured.
        """
        model_info = self.agent.get_model_info()
        
        assert model_info["model_id"] == "us.amazon.nova-premier-v1:0"
        assert model_info["provider"] == "Amazon Bedrock"
        assert model_info["temperature"] == 0.1  # Low temperature for factual responses
        assert model_info["max_tokens"] == 2048
    
    def test_fallback_system_prompt(self):
        """
        Test fallback system prompt when file is not available.
        """
        fallback_prompt = self.agent._get_fallback_system_prompt()
        
        assert "CONTEXT SUPREMACY" in fallback_prompt
        assert "REFUSAL RESPONSES" in fallback_prompt
        assert "This isn't covered in my local context." in fallback_prompt
        assert "I don't have enough local data to answer that." in fallback_prompt
        assert "My knowledge is limited to what's in the context file." in fallback_prompt


if __name__ == "__main__":
    pytest.main([__file__])