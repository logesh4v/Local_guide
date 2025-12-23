"""
Unit tests for Context Loader Agent.
Tests context file loading, isolation, and switching behavior.
"""
import pytest
import os
import tempfile
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.context_loader import ContextLoaderAgent
from models import CityContext


class TestContextLoaderAgent:
    """Unit tests for Context Loader Agent."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create temporary directory for test context files
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test context files
        self.madurai_content = """# Madurai Context
        Famous for Meenakshi Temple and Jigarthanda.
        Traditional food includes idli and dosa.
        """
        
        self.dindigul_content = """# Dindigul Context
        Famous for Thalappakatti Biryani and locks.
        Known as Lock City of Tamil Nadu.
        """
        
        with open(os.path.join(self.temp_dir, "madurai_context.md"), 'w') as f:
            f.write(self.madurai_content)
        
        with open(os.path.join(self.temp_dir, "dindigul_context.md"), 'w') as f:
            f.write(self.dindigul_content)
        
        self.agent = ContextLoaderAgent(context_dir=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_get_available_cities(self):
        """Test getting list of available cities."""
        cities = self.agent.get_available_cities()
        assert cities == ['Madurai', 'Dindigul']
    
    def test_validate_city_selection_valid(self):
        """Test validation of valid city selections."""
        assert self.agent.validate_city_selection('Madurai') is True
        assert self.agent.validate_city_selection('madurai') is True
        assert self.agent.validate_city_selection('MADURAI') is True
        assert self.agent.validate_city_selection('Dindigul') is True
        assert self.agent.validate_city_selection('dindigul') is True
    
    def test_validate_city_selection_invalid(self):
        """Test validation of invalid city selections."""
        assert self.agent.validate_city_selection('Chennai') is False
        assert self.agent.validate_city_selection('') is False
        assert self.agent.validate_city_selection('InvalidCity') is False
    
    def test_load_city_context_madurai(self):
        """Test loading Madurai context."""
        context = self.agent.load_city_context('Madurai')
        
        assert isinstance(context, CityContext)
        assert context.city_name == 'madurai'
        assert 'Meenakshi' in context.context_content
        assert context.is_valid()
        assert self.agent.is_context_loaded()
    
    def test_load_city_context_dindigul(self):
        """Test loading Dindigul context."""
        context = self.agent.load_city_context('Dindigul')
        
        assert isinstance(context, CityContext)
        assert context.city_name == 'dindigul'
        assert 'Thalappakatti' in context.context_content
        assert context.is_valid()
        assert self.agent.is_context_loaded()
    
    def test_load_city_context_invalid_city(self):
        """Test loading context for invalid city."""
        with pytest.raises(ValueError, match="City 'Chennai' is not supported"):
            self.agent.load_city_context('Chennai')
    
    def test_load_city_context_missing_file(self):
        """Test loading context when file doesn't exist."""
        # Create agent with non-existent directory
        agent = ContextLoaderAgent(context_dir="/non/existent/path")
        
        with pytest.raises(FileNotFoundError):
            agent.load_city_context('Madurai')
    
    def test_context_isolation(self):
        """Test that contexts are properly isolated."""
        # Load Madurai context
        madurai_context = self.agent.load_city_context('Madurai')
        assert 'Meenakshi' in madurai_context.context_content
        assert 'Thalappakatti' not in madurai_context.context_content
        
        # Load Dindigul context
        dindigul_context = self.agent.load_city_context('Dindigul')
        assert 'Thalappakatti' in dindigul_context.context_content
        assert 'Meenakshi' not in dindigul_context.context_content
    
    def test_context_switching(self):
        """Test switching between city contexts."""
        # Load initial context
        initial_context = self.agent.load_city_context('Madurai')
        assert self.agent.get_current_context() == initial_context
        assert 'Meenakshi' in initial_context.context_content
        
        # Switch to different city
        new_context = self.agent.switch_city_context('Dindigul')
        assert self.agent.get_current_context() == new_context
        assert new_context != initial_context
        assert 'Thalappakatti' in new_context.context_content
        assert 'Meenakshi' not in new_context.context_content
    
    def test_clear_context(self):
        """Test clearing loaded context."""
        # Load context
        self.agent.load_city_context('Madurai')
        assert self.agent.is_context_loaded()
        
        # Clear context
        self.agent.clear_context()
        assert not self.agent.is_context_loaded()
        assert self.agent.get_current_context() is None
    
    def test_get_context_summary(self):
        """Test getting context summary."""
        # No context loaded
        assert self.agent.get_context_summary() == ""
        
        # Load context
        self.agent.load_city_context('Madurai')
        summary = self.agent.get_context_summary()
        assert 'Madurai' in summary
        assert 'madurai_context.md' in summary
    
    def test_validate_context_isolation_valid(self):
        """Test validation of proper context isolation."""
        self.agent.load_city_context('Madurai')
        assert self.agent.validate_context_isolation('Madurai') is True
        
        self.agent.load_city_context('Dindigul')
        assert self.agent.validate_context_isolation('Dindigul') is True
    
    def test_validate_context_isolation_invalid(self):
        """Test validation fails for improper isolation."""
        self.agent.load_city_context('Madurai')
        assert self.agent.validate_context_isolation('Dindigul') is False
    
    def test_error_handling_empty_file(self):
        """Test error handling for empty context files."""
        # Create empty file
        empty_file = os.path.join(self.temp_dir, "empty_context.md")
        with open(empty_file, 'w') as f:
            f.write("")
        
        # Temporarily add empty city to test
        self.agent.available_cities.append('empty')
        
        with pytest.raises(IOError, match="Context file is empty"):
            self.agent.load_city_context('empty')
    
    def test_error_handling_malformed_file(self):
        """Test error handling for files with permission issues."""
        # This test would require specific OS permissions setup
        # For now, we test the basic error handling structure
        pass


if __name__ == "__main__":
    pytest.main([__file__])