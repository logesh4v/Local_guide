"""
Integration tests for agent pipeline.
Tests end-to-end processing flow, error handling, and agent interaction patterns.
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from local_guide_system import LocalGuideSystem
from models import Query, Response


class TestAgentPipelineIntegration:
    """Integration tests for the complete agent pipeline."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.system = LocalGuideSystem()
        self.system.initialize()
    
    def test_complete_processing_flow_madurai(self):
        """Test complete end-to-end processing flow for Madurai."""
        # Step 1: Select city
        success, message = self.system.select_city("Madurai")
        assert success, f"City selection failed: {message}"
        assert self.system.get_current_city() == "Madurai"
        
        # Step 2: Process a valid food query
        query = "What food is famous in Madurai?"
        
        try:
            response = self.system.process_query(query)
            
            # Verify response structure
            assert isinstance(response, Response)
            assert response.text
            assert response.source_context == "Madurai context"
            
            # Should either be a valid response or standardized refusal
            if response.is_refusal:
                assert response.is_standardized_refusal()
            else:
                assert response.validation_passed
            
        except Exception as e:
            # If AWS connection fails, should still handle gracefully
            if "AWS" in str(e) or "credentials" in str(e):
                pytest.skip(f"AWS connection not available: {e}")
            else:
                raise e
    
    def test_complete_processing_flow_dindigul(self):
        """Test complete end-to-end processing flow for Dindigul."""
        # Step 1: Select city
        success, message = self.system.select_city("Dindigul")
        assert success, f"City selection failed: {message}"
        assert self.system.get_current_city() == "Dindigul"
        
        # Step 2: Process a valid transport query
        query = "How do I get around in Dindigul?"
        
        try:
            response = self.system.process_query(query)
            
            # Verify response structure
            assert isinstance(response, Response)
            assert response.text
            assert response.source_context == "Dindigul context"
            
            # Should either be a valid response or standardized refusal
            if response.is_refusal:
                assert response.is_standardized_refusal()
            else:
                assert response.validation_passed
                
        except Exception as e:
            # If AWS connection fails, should still handle gracefully
            if "AWS" in str(e) or "credentials" in str(e):
                pytest.skip(f"AWS connection not available: {e}")
            else:
                raise e
    
    def test_query_validation_integration(self):
        """Test query validation integration in the pipeline."""
        # Select city first
        self.system.select_city("Madurai")
        
        # Test out-of-scope query
        out_of_scope_query = "What is the latest political news?"
        response = self.system.process_query(out_of_scope_query)
        
        assert response.is_refusal
        assert "supported topics" in response.text.lower()
        
        # Test empty query
        empty_response = self.system.process_query("")
        assert empty_response.is_refusal
    
    def test_context_isolation_integration(self):
        """Test context isolation across city switches."""
        # Start with Madurai
        self.system.select_city("Madurai")
        madurai_query = "What is this place famous for?"
        
        try:
            madurai_response = self.system.process_query(madurai_query)
            
            # Switch to Dindigul
            self.system.switch_city("Dindigul")
            dindigul_response = self.system.process_query(madurai_query)
            
            # Responses should be different (unless both are refusals)
            if not madurai_response.is_refusal and not dindigul_response.is_refusal:
                assert madurai_response.text != dindigul_response.text
                assert madurai_response.source_context != dindigul_response.source_context
                
        except Exception as e:
            if "AWS" in str(e) or "credentials" in str(e):
                pytest.skip(f"AWS connection not available: {e}")
            else:
                raise e
    
    def test_error_handling_no_city_selected(self):
        """Test error handling when no city is selected."""
        # Don't select a city
        response = self.system.process_query("What food is good here?")
        
        assert response.is_refusal
        assert "no city selected" in response.refusal_reason.lower()
    
    def test_error_handling_invalid_city(self):
        """Test error handling for invalid city selection."""
        success, message = self.system.select_city("Chennai")
        
        assert not success
        assert "invalid city" in message.lower()
        assert "chennai" in message.lower()
    
    def test_conversation_history_tracking(self):
        """Test conversation history tracking."""
        self.system.select_city("Madurai")
        
        # Initial history should be empty
        history = self.system.get_conversation_history()
        assert len(history) == 0
        
        # Process a query
        self.system.process_query("Tell me about local food")
        
        # History should now have one entry
        history = self.system.get_conversation_history()
        assert len(history) == 1
        
        query, response = history[0]
        assert isinstance(query, Query)
        assert isinstance(response, Response)
        assert query.text == "Tell me about local food"
    
    def test_system_status_reporting(self):
        """Test system status reporting."""
        status = self.system.get_system_status()
        
        assert 'initialized' in status
        assert 'available_cities' in status
        assert 'model_info' in status
        
        # Before city selection
        assert status['selected_city'] is None
        assert not status['context_loaded']
        
        # After city selection
        self.system.select_city("Madurai")
        status = self.system.get_system_status()
        
        assert status['selected_city'] == "Madurai"
        assert status['context_loaded']
    
    def test_health_check_integration(self):
        """Test system health check."""
        health = self.system.validate_system_health()
        
        assert 'overall_status' in health
        assert 'components' in health
        assert 'issues' in health
        
        # Should have all expected components
        expected_components = [
            'context_loader', 
            'query_validator', 
            'local_guide', 
            'guard_agent'
        ]
        
        for component in expected_components:
            assert component in health['components']
    
    def test_usage_statistics_tracking(self):
        """Test usage statistics tracking."""
        self.system.select_city("Madurai")
        
        # Initial stats
        stats = self.system.get_usage_statistics()
        assert stats['total_queries'] == 0
        
        # Process some queries
        self.system.process_query("What food is good?")
        self.system.process_query("Invalid political question")
        
        # Check updated stats
        stats = self.system.get_usage_statistics()
        assert stats['total_queries'] == 2
        assert stats['current_city'] == "Madurai"
    
    def test_session_reset_integration(self):
        """Test session reset functionality."""
        # Set up a session
        self.system.select_city("Madurai")
        self.system.process_query("What food is good?")
        
        # Verify session state
        assert self.system.get_current_city() == "Madurai"
        assert len(self.system.get_conversation_history()) == 1
        
        # Reset session
        self.system.reset_session()
        
        # Verify reset
        assert self.system.get_current_city() is None
        assert len(self.system.get_conversation_history()) == 0
    
    def test_agent_interaction_patterns(self):
        """Test interaction patterns between agents."""
        self.system.select_city("Madurai")
        
        # Test that all agents are involved in processing
        with patch.object(self.system.query_validator, 'create_validation_response') as mock_validator:
            with patch.object(self.system.local_guide, 'create_response_object') as mock_guide:
                with patch.object(self.system.guard_agent, 'validate_response_object') as mock_guard:
                    
                    # Set up mocks
                    mock_validator.return_value = Query(
                        text="test query",
                        city="Madurai",
                        is_valid=True
                    )
                    
                    mock_guide.return_value = Response(
                        text="test response",
                        is_refusal=False,
                        source_context="Madurai context"
                    )
                    
                    mock_guard.return_value = Response(
                        text="test response",
                        is_refusal=False,
                        source_context="Madurai context",
                        validation_passed=True
                    )
                    
                    # Process query
                    response = self.system.process_query("test query")
                    
                    # Verify all agents were called
                    mock_validator.assert_called_once()
                    mock_guide.assert_called_once()
                    mock_guard.assert_called_once()
    
    def test_error_recovery_mechanisms(self):
        """Test error recovery mechanisms."""
        self.system.select_city("Madurai")
        
        # Test recovery from agent failures
        with patch.object(self.system.local_guide, 'create_response_object') as mock_guide:
            # Simulate agent failure
            mock_guide.side_effect = Exception("Simulated failure")
            
            response = self.system.process_query("test query")
            
            # Should recover with a refusal response
            assert response.is_refusal
            assert response.is_standardized_refusal()
    
    def test_concurrent_query_handling(self):
        """Test handling of multiple queries in sequence."""
        self.system.select_city("Madurai")
        
        queries = [
            "What food is good?",
            "How do I get around?",
            "What does 'enna da' mean?",
            "Is it safe at night?",
            "What festivals are celebrated?"
        ]
        
        responses = []
        for query in queries:
            try:
                response = self.system.process_query(query)
                responses.append(response)
                assert isinstance(response, Response)
            except Exception as e:
                if "AWS" in str(e) or "credentials" in str(e):
                    pytest.skip(f"AWS connection not available: {e}")
                else:
                    raise e
        
        # All responses should be valid Response objects
        assert len(responses) == len(queries)
        
        # Conversation history should track all queries
        history = self.system.get_conversation_history()
        assert len(history) == len(queries)


if __name__ == "__main__":
    pytest.main([__file__])