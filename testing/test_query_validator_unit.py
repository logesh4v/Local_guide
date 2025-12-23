"""
Unit tests for Query Validation Agent.
Tests acceptance of supported topic queries, rejection of out-of-scope queries,
and edge cases with empty or malformed queries.
"""
import pytest
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.query_validator import QueryValidationAgent
from models import Query


class TestQueryValidationAgentUnit:
    """Unit tests for Query Validation Agent."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = QueryValidationAgent()
    
    def test_get_supported_topics(self):
        """Test getting list of supported topics."""
        topics = self.validator.get_supported_topics()
        expected_topics = ['food', 'transport', 'slang', 'safety', 'lifestyle']
        assert topics == expected_topics
        
        # Ensure returned list is a copy (immutable)
        topics.append('new_topic')
        assert len(self.validator.get_supported_topics()) == 5
    
    def test_food_topic_queries_accepted(self):
        """Test acceptance of food-related queries."""
        food_queries = [
            "Where can I find good biryani?",
            "What is the best restaurant in town?",
            "Tell me about local food specialties",
            "I want to eat traditional dishes",
            "Can you recommend a good mess?",
            "What is jigarthanda?",
            "Where to get thalappakatti biryani?"
        ]
        
        for query in food_queries:
            assert self.validator.validate_query_scope(query), f"Food query should be accepted: {query}"
            assert self.validator.is_supported_topic(query), f"Should identify as supported topic: {query}"
            topic = self.validator.identify_topic(query)
            assert topic == 'food', f"Should identify as food topic: {query}"
    
    def test_transport_topic_queries_accepted(self):
        """Test acceptance of transport-related queries."""
        transport_queries = [
            "How do I get to the railway station?",
            "What is the bus fare?",
            "Are auto rickshaws available?",
            "Tell me about local transport",
            "Which route should I take?",
            "How to travel to nearby cities?",
            "What time does the last bus run?"
        ]
        
        for query in transport_queries:
            assert self.validator.validate_query_scope(query), f"Transport query should be accepted: {query}"
            topic = self.validator.identify_topic(query)
            assert topic == 'transport', f"Should identify as transport topic: {query}"
    
    def test_slang_topic_queries_accepted(self):
        """Test acceptance of slang/language-related queries."""
        slang_queries = [
            "What does 'enna da' mean?",
            "How do people greet each other?",
            "What are common Tamil phrases?",
            "How to say hello in local language?",
            "What is the local dialect like?",
            "Teach me some local expressions",
            "How do locals speak?"
        ]
        
        for query in slang_queries:
            assert self.validator.validate_query_scope(query), f"Slang query should be accepted: {query}"
            topic = self.validator.identify_topic(query)
            assert topic == 'slang', f"Should identify as slang topic: {query}"
    
    def test_safety_topic_queries_accepted(self):
        """Test acceptance of safety-related queries."""
        safety_queries = [
            "Is this area safe at night?",
            "What precautions should I take?",
            "Are there any dangerous areas?",
            "Emergency contact numbers?",
            "Where is the nearest police station?",
            "How safe is public transport?",
            "What should tourists be careful about?"
        ]
        
        for query in safety_queries:
            assert self.validator.validate_query_scope(query), f"Safety query should be accepted: {query}"
            topic = self.validator.identify_topic(query)
            assert topic == 'safety', f"Should identify as safety topic: {query}"
    
    def test_lifestyle_topic_queries_accepted(self):
        """Test acceptance of lifestyle/culture-related queries."""
        lifestyle_queries = [
            "What festivals are celebrated here?",
            "Tell me about local customs",
            "What is the shopping culture like?",
            "How do people dress traditionally?",
            "What are the local traditions?",
            "When do shops close?",
            "What is the weather like?"
        ]
        
        for query in lifestyle_queries:
            assert self.validator.validate_query_scope(query), f"Lifestyle query should be accepted: {query}"
            topic = self.validator.identify_topic(query)
            assert topic == 'lifestyle', f"Should identify as lifestyle topic: {query}"
    
    def test_out_of_scope_queries_rejected(self):
        """Test rejection of out-of-scope queries."""
        out_of_scope_queries = [
            "What is the latest political news?",
            "Can you diagnose my medical condition?",
            "Help me with legal advice",
            "What are the stock market trends?",
            "Teach me programming",
            "What is the weather in New York?",
            "Who won the cricket match yesterday?"
        ]
        
        for query in out_of_scope_queries:
            assert not self.validator.validate_query_scope(query), f"Out-of-scope query should be rejected: {query}"
            assert not self.validator.is_supported_topic(query), f"Should not identify as supported topic: {query}"
            
            reason = self.validator.get_rejection_reason(query)
            assert "supported topics" in reason.lower(), f"Rejection reason should mention supported topics: {query}"
    
    def test_empty_queries_rejected(self):
        """Test rejection of empty or whitespace queries."""
        empty_queries = ["", "   ", "\t", "\n", "  \t\n  "]
        
        for query in empty_queries:
            assert not self.validator.validate_query_scope(query), f"Empty query should be rejected: '{query}'"
            
            reason = self.validator.get_rejection_reason(query)
            assert "empty" in reason.lower() or "whitespace" in reason.lower(), f"Should mention empty/whitespace: '{query}'"
    
    def test_special_character_queries_rejected(self):
        """Test rejection of queries with only special characters."""
        special_queries = ["!@#$%", "123456", "???", "...", "---"]
        
        for query in special_queries:
            assert not self.validator.validate_query_scope(query), f"Special character query should be rejected: {query}"
            
            reason = self.validator.get_rejection_reason(query)
            assert reason, f"Should provide rejection reason for: {query}"
    
    def test_overly_long_queries_rejected(self):
        """Test rejection of overly long queries."""
        long_query = "food " * 300  # Creates a 1500+ character query
        
        assert not self.validator.validate_query_scope(long_query), "Overly long query should be rejected"
        
        reason = self.validator.get_rejection_reason(long_query)
        assert "too long" in reason.lower(), "Should mention query is too long"
    
    def test_query_preprocessing(self):
        """Test query preprocessing functionality."""
        test_cases = [
            ("  hello   world  ", "hello world"),
            ("food!!!!!!", "food?"),
            ("what about food......", "what about food..."),
            ("", ""),
            ("   ", "")
        ]
        
        for input_query, expected in test_cases:
            processed = self.validator.preprocess_query(input_query)
            assert processed == expected, f"Expected '{expected}', got '{processed}' for input '{input_query}'"
    
    def test_topic_suggestions(self):
        """Test topic suggestions for out-of-scope queries."""
        # Test with completely unrelated query
        suggestions = self.validator.get_topic_suggestions("quantum physics")
        assert len(suggestions) > 0, "Should provide topic suggestions"
        assert all(topic in self.validator.get_supported_topics() for topic in suggestions)
        
        # Test with partially related query
        suggestions = self.validator.get_topic_suggestions("eating politics")
        assert 'food' in suggestions, "Should suggest food topic for eating-related query"
    
    def test_create_validation_response(self):
        """Test creation of validated Query objects."""
        # Valid query
        query_obj = self.validator.create_validation_response("Where can I eat?", "Madurai")
        assert isinstance(query_obj, Query)
        assert query_obj.is_valid
        assert query_obj.validation_reason is None
        assert query_obj.city == "Madurai"
        assert query_obj.text == "Where can I eat?"
        
        # Invalid query
        query_obj = self.validator.create_validation_response("", "Dindigul")
        assert isinstance(query_obj, Query)
        assert not query_obj.is_valid
        assert query_obj.validation_reason is not None
        assert query_obj.city == "Dindigul"
    
    def test_validate_query_object(self):
        """Test validation of Query objects."""
        # Valid query object
        valid_query = Query(
            text="Tell me about local food",
            city="Madurai",
            timestamp=datetime.now(),
            is_valid=True
        )
        
        is_valid, reason = self.validator.validate_query_object(valid_query)
        assert is_valid
        assert reason is None
        
        # Empty query object
        empty_query = Query(
            text="",
            city="Madurai",
            timestamp=datetime.now(),
            is_valid=False
        )
        
        is_valid, reason = self.validator.validate_query_object(empty_query)
        assert not is_valid
        assert reason == "Query is empty."
        
        # Out-of-scope query object
        invalid_query = Query(
            text="Tell me about politics",
            city="Dindigul",
            timestamp=datetime.now(),
            is_valid=False
        )
        
        is_valid, reason = self.validator.validate_query_object(invalid_query)
        assert not is_valid
        assert reason is not None
        assert "supported topics" in reason
    
    def test_case_insensitive_validation(self):
        """Test that validation is case-insensitive."""
        queries = [
            "FOOD",
            "Food",
            "food",
            "FoOd",
            "WHERE CAN I EAT?",
            "where can i eat?"
        ]
        
        for query in queries:
            assert self.validator.validate_query_scope(query), f"Should accept case variations: {query}"
            assert self.validator.is_supported_topic(query), f"Should identify topic for: {query}"


if __name__ == "__main__":
    pytest.main([__file__])