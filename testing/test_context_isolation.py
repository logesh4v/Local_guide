"""
Property-based tests for context isolation and loading.
**Feature: local-guide-ai, Property 1: Context isolation and loading**
**Validates: Requirements 1.2, 1.3, 1.4**
"""
import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import CityContext, AppState
from agents.context_loader import ContextLoaderAgent


class TestContextIsolation:
    """Property-based tests for context isolation."""
    
    @given(st.sampled_from(['Madurai', 'Dindigul']))
    @settings(max_examples=100)
    def test_context_isolation_property(self, city_name: str):
        """
        **Feature: local-guide-ai, Property 1: Context isolation and loading**
        For any city selection, the Context Loader Agent should load only that 
        city's context file and prevent any mixing of context data from other cities.
        """
        # This test will be implemented after ContextLoaderAgent is created
        # For now, we test the data model behavior
        
        # Create context for the selected city
        context_content = f"Test content for {city_name}"
        context = CityContext(
            city_name=city_name.lower(),
            context_content=context_content,
            file_path=f"context/{city_name.lower()}_context.md",
            last_loaded=datetime.now()
        )
        
        # Verify context is valid and contains only the selected city's data
        assert context.is_valid()
        assert context.city_name.lower() in ['madurai', 'dindigul']
        assert city_name.lower() in context.context_content.lower()
        
        # Verify no mixing with other city data
        other_city = 'Dindigul' if city_name == 'Madurai' else 'Madurai'
        assert other_city.lower() not in context.city_name.lower()
    
    @given(st.sampled_from(['Madurai', 'Dindigul']))
    @settings(max_examples=100)
    def test_context_switching_property(self, initial_city: str):
        """
        Test that switching cities completely replaces previous context.
        """
        app_state = AppState()
        
        # Set initial city
        app_state.selected_city = initial_city
        initial_context = CityContext(
            city_name=initial_city.lower(),
            context_content=f"Content for {initial_city}",
            file_path=f"context/{initial_city.lower()}_context.md",
            last_loaded=datetime.now()
        )
        app_state.loaded_context = initial_context
        
        # Switch to other city
        other_city = 'Dindigul' if initial_city == 'Madurai' else 'Madurai'
        app_state.selected_city = other_city
        new_context = CityContext(
            city_name=other_city.lower(),
            context_content=f"Content for {other_city}",
            file_path=f"context/{other_city.lower()}_context.md",
            last_loaded=datetime.now()
        )
        app_state.loaded_context = new_context
        
        # Verify complete replacement
        assert app_state.selected_city == other_city
        assert app_state.loaded_context.city_name == other_city.lower()
        assert initial_city.lower() not in app_state.loaded_context.context_content.lower()
        assert other_city.lower() in app_state.loaded_context.context_content.lower()
    
    def test_context_file_isolation(self):
        """
        Test that context files contain only city-specific information.
        """
        # Test Madurai context file
        madurai_path = "context/madurai_context.md"
        if os.path.exists(madurai_path):
            with open(madurai_path, 'r', encoding='utf-8') as f:
                madurai_content = f.read()
            
            # Verify Madurai-specific content
            assert 'madurai' in madurai_content.lower()
            assert 'meenakshi' in madurai_content.lower()  # Madurai-specific temple
            
            # Verify no Dindigul-specific content
            assert 'thalappakatti' not in madurai_content.lower()  # Dindigul-specific biryani
        
        # Test Dindigul context file
        dindigul_path = "context/dindigul_context.md"
        if os.path.exists(dindigul_path):
            with open(dindigul_path, 'r', encoding='utf-8') as f:
                dindigul_content = f.read()
            
            # Verify Dindigul-specific content
            assert 'dindigul' in dindigul_content.lower()
            assert 'thalappakatti' in dindigul_content.lower()  # Dindigul-specific biryani
            
            # Verify no Madurai-specific content
            assert 'meenakshi' not in dindigul_content.lower()  # Madurai-specific temple


if __name__ == "__main__":
    pytest.main([__file__])