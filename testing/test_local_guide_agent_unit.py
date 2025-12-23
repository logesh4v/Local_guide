"""
Unit tests for Local Guide Agent.
Tests response generation, model configuration, and Bedrock integration.
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.local_guide_agent import LocalGuideAgent
from models import Response


class TestLocalGuideAgentUnit:
    """Unit tests for Local Guide Agent."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.agent = LocalGuideAgent()
        
        # Sample contexts for testing
        self.madurai_context = """# Madurai Context
        Famous for Meenakshi Temple and Jigarthanda.
        Traditional food includes idli, dosa, and biryani.
        Local transport includes buses and auto rickshaws.
        Popular restaurants: Murugan Idli Shop, Kumar Mess.
        """
        
        self.dindigul_context = """# Dindigul Context
        Famous for Thalappakatti Biryani and lock manufacturing.
        Known as Lock City of Tamil Nadu.
        Local specialties include mutton biryani and vada curry.
        Popular restaurants: Thalappakatti Restaurant, Hotel Selvam.
        """
    
    def test_model_configuration(self):
        """Test model configuration with Nova Premier."""
        model_info = self.agent.get_model_info()
        
        assert model_info["model_id"] == "us.amazon.nova-premier-v1:0"
        assert model_info["provider"] == "Amazon Bedrock"
        assert model_info["temperature"] == 0.1
        assert model_info["max_tokens"] == 2048
        assert "region" in model_info
    
    def test_system_prompt_loading(self):
        """Test system prompt loading from file."""
        # Test that system prompt contains required elements
        prompt = self.agent.system_prompt_template
        
        assert "CONTEXT SUPREMACY" in prompt
        assert "REFUSAL RESPONSES" in prompt
        assert "This isn't covered in my local context." in prompt
        assert "I don't have enough local data to answer that." in prompt
        assert "My knowledge is limited to what's in the context file." in prompt
    
    def test_fallback_system_prompt(self):
        """Test fallback system prompt when file loading fails."""
        fallback_prompt = self.agent._get_fallback_system_prompt()
        
        assert "CONTEXT SUPREMACY" in fallback_prompt
        assert "REFUSAL RESPONSES" in fallback_prompt
        assert len(fallback_prompt) > 100  # Should be substantial
    
    def test_apply_system_prompt_with_context(self):
        """Test applying system prompt with city context."""
        context = self.madurai_context
        full_prompt = self.agent.apply_system_prompt(context)
        
        # Should contain original system prompt
        assert "CONTEXT SUPREMACY" in full_prompt
        
        # Should contain the provided context
        assert "Meenakshi Temple" in full_prompt
        assert "CITY CONTEXT:" in full_prompt
        assert "Use ONLY the information provided in the CITY CONTEXT" in full_prompt
    
    @patch('agents.local_guide_agent.Agent')
    def test_generate_response_with_valid_input(self, mock_agent_class):
        """Test response generation with valid query and context."""
        # Mock the agent response
        mock_agent_instance = Mock()
        mock_agent_instance.return_value = "Madurai is famous for Meenakshi Temple and Jigarthanda."
        mock_agent_class.return_value = mock_agent_instance
        
        query = "What is this place famous for?"
        response = self.agent.generate_response(query, self.madurai_context)
        
        assert response == "Madurai is famous for Meenakshi Temple and Jigarthanda."
        mock_agent_class.assert_called_once()
        mock_agent_instance.assert_called_once_with(query)
    
    def test_generate_response_empty_query(self):
        """Test response generation with empty query."""
        response = self.agent.generate_response("", self.madurai_context)
        assert response == "This isn't covered in my local context."
        
        response = self.agent.generate_response("   ", self.madurai_context)
        assert response == "This isn't covered in my local context."
    
    def test_generate_response_empty_context(self):
        """Test response generation with empty context."""
        query = "What food is famous here?"
        
        response = self.agent.generate_response(query, "")
        assert response == "I don't have enough local data to answer that."
        
        response = self.agent.generate_response(query, None)
        assert response == "I don't have enough local data to answer that."
    
    @patch('agents.local_guide_agent.Agent')
    def test_generate_response_with_exception(self, mock_agent_class):
        """Test response generation when an exception occurs."""
        # Mock agent to raise an exception
        mock_agent_instance = Mock()
        mock_agent_instance.side_effect = Exception("API Error")
        mock_agent_class.return_value = mock_agent_instance
        
        query = "What food is famous here?"
        response = self.agent.generate_response(query, self.madurai_context)
        
        assert response == "My knowledge is limited to what's in the context file."
    
    @patch('agents.local_guide_agent.Agent')
    def test_create_response_object_normal_response(self, mock_agent_class):
        """Test creation of Response object with normal response."""
        # Mock normal response
        mock_agent_instance = Mock()
        mock_agent_instance.return_value = "Madurai is famous for Meenakshi Temple."
        mock_agent_class.return_value = mock_agent_instance
        
        query = "What is famous here?"
        response_obj = self.agent.create_response_object(query, self.madurai_context, "Madurai")
        
        assert isinstance(response_obj, Response)
        assert response_obj.text == "Madurai is famous for Meenakshi Temple."
        assert not response_obj.is_refusal
        assert response_obj.refusal_reason is None
        assert response_obj.source_context == "Madurai context"
        assert response_obj.validation_passed is True
    
    def test_create_response_object_refusal_response(self):
        """Test creation of Response object with refusal response."""
        query = "What is famous here?"
        response_obj = self.agent.create_response_object(query, "", "Madurai")
        
        assert isinstance(response_obj, Response)
        assert response_obj.is_refusal
        assert response_obj.refusal_reason == "Information not available in context"
        assert response_obj.source_context == "Madurai context"
        assert response_obj.is_standardized_refusal()
    
    def test_validate_response_against_context_valid(self):
        """Test validation of valid responses against context."""
        context = self.madurai_context
        
        # Response with context words
        valid_response = "Madurai is famous for Meenakshi Temple and Jigarthanda."
        assert self.agent.validate_response_against_context(valid_response, context)
        
        # Response with some context words
        partial_response = "The temple here is very famous and attracts many visitors."
        assert self.agent.validate_response_against_context(partial_response, context)
    
    def test_validate_response_against_context_invalid(self):
        """Test validation of invalid responses against context."""
        context = self.madurai_context
        
        # Response with no context words
        invalid_response = "This city has many shopping malls and modern buildings."
        assert not self.agent.validate_response_against_context(invalid_response, context)
        
        # Empty response
        assert not self.agent.validate_response_against_context("", context)
        assert not self.agent.validate_response_against_context(None, context)
    
    def test_validate_response_against_context_refusal(self):
        """Test validation of refusal responses (always valid)."""
        context = self.madurai_context
        
        refusal_responses = [
            "This isn't covered in my local context.",
            "I don't have enough local data to answer that.",
            "My knowledge is limited to what's in the context file."
        ]
        
        for refusal in refusal_responses:
            assert self.agent.validate_response_against_context(refusal, context)
    
    def test_validate_response_against_context_edge_cases(self):
        """Test validation edge cases."""
        # Empty context
        response = "Some response text"
        assert not self.agent.validate_response_against_context(response, "")
        assert not self.agent.validate_response_against_context(response, None)
        
        # Response with only common words
        common_response = "The and or but in on at to for of with by is are"
        assert not self.agent.validate_response_against_context(common_response, self.madurai_context)
    
    @patch('agents.local_guide_agent.Agent')
    def test_model_connection_test_success(self, mock_agent_class):
        """Test successful model connection test."""
        # Mock successful response
        mock_agent_instance = Mock()
        mock_agent_instance.return_value = "Test response"
        mock_agent_class.return_value = mock_agent_instance
        
        result = self.agent.test_model_connection()
        assert result is True
    
    @patch('agents.local_guide_agent.Agent')
    def test_model_connection_test_failure(self, mock_agent_class):
        """Test failed model connection test."""
        # Mock exception
        mock_agent_instance = Mock()
        mock_agent_instance.side_effect = Exception("Connection failed")
        mock_agent_class.return_value = mock_agent_instance
        
        result = self.agent.test_model_connection()
        assert result is False
    
    def test_response_text_extraction(self):
        """Test extraction of text from different response types."""
        # Test with string response
        with patch.object(self.agent, 'agent') as mock_agent:
            mock_agent.return_value = "Simple string response"
            response = self.agent.generate_response("test", self.madurai_context)
            assert response == "Simple string response"
        
        # Test with object response having text attribute
        with patch.object(self.agent, 'agent') as mock_agent:
            mock_response = Mock()
            mock_response.text = "Response with text attribute"
            mock_agent.return_value = mock_response
            response = self.agent.generate_response("test", self.madurai_context)
            assert response == "Response with text attribute"
    
    def test_context_isolation_in_responses(self):
        """Test that responses don't mix context from different cities."""
        # This test would require actual API calls or more sophisticated mocking
        # For now, we test the validation logic
        
        madurai_response = "Madurai is famous for Meenakshi Temple and Jigarthanda."
        dindigul_response = "Dindigul is famous for Thalappakatti Biryani and locks."
        
        # Madurai response should validate against Madurai context
        assert self.agent.validate_response_against_context(madurai_response, self.madurai_context)
        
        # Dindigul response should validate against Dindigul context
        assert self.agent.validate_response_against_context(dindigul_response, self.dindigul_context)
        
        # Cross-validation should have lower scores (but might still pass basic validation)
        # This is a limitation of the basic validation - the Guard Agent will provide more sophisticated validation
    
    def test_system_prompt_context_injection(self):
        """Test that context is properly injected into system prompt."""
        test_context = "Test city context with specific information."
        full_prompt = self.agent.apply_system_prompt(test_context)
        
        # Should contain both system prompt and context
        assert "CONTEXT SUPREMACY" in full_prompt
        assert "Test city context with specific information." in full_prompt
        assert "CITY CONTEXT:" in full_prompt
        assert "Use ONLY the information provided in the CITY CONTEXT above" in full_prompt


if __name__ == "__main__":
    pytest.main([__file__])