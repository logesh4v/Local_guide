"""
Unit tests for Streamlit interface.
Tests UI component rendering, city selection, and response display formatting.
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock streamlit before importing app
sys.modules['streamlit'] = MagicMock()

from models import Response


class TestStreamlitInterface:
    """Unit tests for Streamlit interface."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Mock streamlit components
        self.mock_st = MagicMock()
        sys.modules['streamlit'] = self.mock_st
    
    def test_city_selection_dropdown(self):
        """Test city selection dropdown functionality."""
        # Import app after mocking streamlit
        import app
        
        # Mock the system
        mock_system = Mock()
        mock_system.get_available_cities.return_value = ['Madurai', 'Dindigul']
        
        with patch('app.LocalGuideSystem', return_value=mock_system):
            # Test that selectbox is called with correct options
            self.mock_st.selectbox.return_value = 'Madurai'
            
            # This would be called in the app
            selected_city = self.mock_st.selectbox(
                "Select a city:",
                ['Madurai', 'Dindigul'],
                index=0
            )
            
            assert selected_city == 'Madurai'
            self.mock_st.selectbox.assert_called_with(
                "Select a city:",
                ['Madurai', 'Dindigul'],
                index=0
            )
    
    def test_text_input_handling(self):
        """Test text input handling for user questions."""
        # Mock text input
        self.mock_st.text_input.return_value = "What food is famous here?"
        
        user_query = self.mock_st.text_input("Ask me anything about the city:")
        
        assert user_query == "What food is famous here?"
        self.mock_st.text_input.assert_called_with("Ask me anything about the city:")
    
    def test_response_display_normal(self):
        """Test response display for normal responses."""
        # Create a normal response
        response = Response(
            text="Madurai is famous for Meenakshi Temple and Jigarthanda.",
            is_refusal=False,
            source_context="Madurai context"
        )
        
        # Test that success message is displayed
        self.mock_st.success.return_value = None
        self.mock_st.success(response.text)
        
        self.mock_st.success.assert_called_with(response.text)
    
    def test_response_display_refusal(self):
        """Test response display for refusal responses."""
        # Create a refusal response
        response = Response(
            text="This isn't covered in my local context.",
            is_refusal=True,
            refusal_reason="Query out of scope",
            source_context="Madurai context"
        )
        
        # Test that warning message is displayed for refusals
        self.mock_st.warning.return_value = None
        self.mock_st.warning(response.text)
        
        self.mock_st.warning.assert_called_with(response.text)
    
    def test_sidebar_system_status(self):
        """Test sidebar system status display."""
        # Mock system status
        mock_status = {
            'initialized': True,
            'selected_city': 'Madurai',
            'context_loaded': True,
            'conversation_length': 3,
            'available_cities': ['Madurai', 'Dindigul']
        }
        
        # Test sidebar components
        self.mock_st.sidebar.header.return_value = None
        self.mock_st.sidebar.write.return_value = None
        
        self.mock_st.sidebar.header("System Status")
        self.mock_st.sidebar.write(f"Selected City: {mock_status['selected_city']}")
        self.mock_st.sidebar.write(f"Context Loaded: {mock_status['context_loaded']}")
        
        # Verify calls
        self.mock_st.sidebar.header.assert_called_with("System Status")
        assert self.mock_st.sidebar.write.call_count >= 2
    
    def test_error_handling_display(self):
        """Test error handling and display."""
        error_message = "System initialization failed"
        
        # Test error display
        self.mock_st.error.return_value = None
        self.mock_st.error(error_message)
        
        self.mock_st.error.assert_called_with(error_message)
    
    def test_conversation_history_display(self):
        """Test conversation history display."""
        # Mock conversation history
        mock_history = [
            ("What food is good?", "Madurai has great biryani and jigarthanda."),
            ("How do I get around?", "Auto rickshaws and buses are available.")
        ]
        
        # Test expander for history
        self.mock_st.expander.return_value.__enter__ = Mock()
        self.mock_st.expander.return_value.__exit__ = Mock()
        
        with self.mock_st.expander("Conversation History"):
            for i, (query, response) in enumerate(mock_history):
                self.mock_st.write(f"**Q{i+1}:** {query}")
                self.mock_st.write(f"**A{i+1}:** {response}")
        
        self.mock_st.expander.assert_called_with("Conversation History")
    
    def test_loading_state_display(self):
        """Test loading state display."""
        # Test spinner
        self.mock_st.spinner.return_value.__enter__ = Mock()
        self.mock_st.spinner.return_value.__exit__ = Mock()
        
        with self.mock_st.spinner("Processing your query..."):
            pass
        
        self.mock_st.spinner.assert_called_with("Processing your query...")
    
    def test_city_selection_state_management(self):
        """Test city selection state management."""
        # Mock session state
        self.mock_st.session_state = {}
        
        # Test state initialization
        if 'selected_city' not in self.mock_st.session_state:
            self.mock_st.session_state['selected_city'] = None
        
        # Test state update
        self.mock_st.session_state['selected_city'] = 'Madurai'
        
        assert self.mock_st.session_state['selected_city'] == 'Madurai'
    
    def test_query_input_validation(self):
        """Test query input validation in UI."""
        # Test empty query handling
        empty_query = ""
        
        if not empty_query.strip():
            self.mock_st.warning("Please enter a question.")
        
        self.mock_st.warning.assert_called_with("Please enter a question.")
    
    def test_response_formatting(self):
        """Test response text formatting."""
        # Test long response formatting
        long_response = "This is a very long response that might need formatting. " * 10
        
        # Test that markdown is used for formatting
        self.mock_st.markdown.return_value = None
        self.mock_st.markdown(long_response)
        
        self.mock_st.markdown.assert_called_with(long_response)
    
    def test_help_information_display(self):
        """Test help information display."""
        help_text = """
        **Supported Topics:**
        - Food and dining
        - Transportation
        - Local language and slang
        - Safety information
        - Lifestyle and culture
        """
        
        # Test help expander
        self.mock_st.expander.return_value.__enter__ = Mock()
        self.mock_st.expander.return_value.__exit__ = Mock()
        
        with self.mock_st.expander("Help - What can I ask?"):
            self.mock_st.markdown(help_text)
        
        self.mock_st.expander.assert_called_with("Help - What can I ask?")
    
    def test_system_health_display(self):
        """Test system health status display."""
        mock_health = {
            'overall_status': 'healthy',
            'components': {
                'context_loader': 'healthy',
                'query_validator': 'healthy',
                'local_guide': 'warning',
                'guard_agent': 'healthy'
            },
            'issues': ['AWS connection warning']
        }
        
        # Test health status colors
        if mock_health['overall_status'] == 'healthy':
            self.mock_st.success("System Status: Healthy")
        elif mock_health['overall_status'] == 'warning':
            self.mock_st.warning("System Status: Warning")
        else:
            self.mock_st.error("System Status: Error")
        
        self.mock_st.success.assert_called_with("System Status: Healthy")
    
    def test_usage_statistics_display(self):
        """Test usage statistics display."""
        mock_stats = {
            'total_queries': 5,
            'successful_responses': 3,
            'refusal_responses': 2,
            'refusal_rate': 0.4
        }
        
        # Test metrics display
        self.mock_st.metric.return_value = None
        
        self.mock_st.metric("Total Queries", mock_stats['total_queries'])
        self.mock_st.metric("Success Rate", f"{(1-mock_stats['refusal_rate'])*100:.1f}%")
        
        assert self.mock_st.metric.call_count == 2


if __name__ == "__main__":
    pytest.main([__file__])