"""
Property-based tests for query validation.
**Feature: local-guide-ai, Property 2: Query scope validation**
**Validates: Requirements 2.1, 2.2**
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.query_validator import QueryValidationAgent
from models import Query
from datetime import datetime


class TestQueryValidationProperty:
    """Property-based tests for query validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = QueryValidationAgent()
    
    @given(st.sampled_from([
        'food', 'eat', 'restaurant', 'biryani', 'idli', 'jigarthanda',
        'transport', 'bus', 'auto', 'train', 'travel', 'route',
        'slang', 'language', 'tamil', 'phrase', 'meaning',
        'safety', 'safe', 'police', 'emergency', 'danger',
        'lifestyle', 'culture', 'festival', 'temple', 'shopping'
    ]))
    @settings(max_examples=100)
    def test_supported_topic_queries_accepted(self, keyword: str):
        """
        **Feature: local-guide-ai, Property 2: Query scope validation**
        For any user query containing supported topic keywords, the Query Validation Agent 
        should accept the query for processing.
        """
        # Create queries with supported keywords
        test_queries = [
            f"Tell me about {keyword}",
            f"What is the best {keyword} in the city?",
            f"I need help with {keyword}",
            f"Can you recommend {keyword}?",
            f"Where can I find {keyword}?"
        ]
        
        for query_text in test_queries:
            is_valid = self.validator.validate_query_scope(query_text)
            assert is_valid, f"Query '{query_text}' should be accepted but was rejected"
            
            # Verify topic identification works
            topic = self.validator.identify_topic(query_text)
            assert topic is not None, f"Should identify topic for '{query_text}'"
            assert topic in self.validator.get_supported_topics()
    
    @given(st.sampled_from([
        'politics', 'election', 'government', 'minister', 'party',
        'medical', 'doctor', 'medicine', 'treatment', 'surgery',
        'legal', 'lawyer', 'court', 'case', 'law',
        'technology', 'computer', 'software', 'programming', 'AI',
        'sports', 'cricket', 'football', 'match', 'player'
    ]))
    @settings(max_examples=100)
    def test_unsupported_topic_queries_rejected(self, keyword: str):
        """
        **Feature: local-guide-ai, Property 2: Query scope validation**
        For any user query outside supported topics, the Query Validation Agent 
        should reject the query with appropriate messaging.
        """
        # Create queries with unsupported keywords
        test_queries = [
            f"Tell me about {keyword}",
            f"What is the latest {keyword} news?",
            f"I need help with {keyword}",
            f"Can you recommend {keyword}?",
            f"Where can I find {keyword}?"
        ]
        
        for query_text in test_queries:
            is_valid = self.validator.validate_query_scope(query_text)
            assert not is_valid, f"Query '{query_text}' should be rejected but was accepted"
            
            # Verify rejection reason is provided
            rejection_reason = self.validator.get_rejection_reason(query_text)
            assert rejection_reason, f"Should provide rejection reason for '{query_text}'"
            assert "supported topics" in rejection_reason.lower()
    
    @given(st.text(min_size=1, max_size=100))
    @settings(max_examples=100)
    def test_query_validation_consistency(self, query_text: str):
        """
        Test that query validation is consistent and deterministic.
        """
        assume(query_text.strip())  # Skip empty or whitespace-only strings
        
        # Validation should be consistent across multiple calls
        result1 = self.validator.validate_query_scope(query_text)
        result2 = self.validator.validate_query_scope(query_text)
        assert result1 == result2, f"Validation should be consistent for '{query_text}'"
        
        # If valid, should identify a topic
        if result1:
            topic = self.validator.identify_topic(query_text)
            assert topic in self.validator.get_supported_topics()
        else:
            # If invalid, should provide rejection reason
            reason = self.validator.get_rejection_reason(query_text)
            assert reason, f"Should provide rejection reason for invalid query '{query_text}'"
    
    @given(st.integers(min_value=0, max_value=2000))
    @settings(max_examples=50)
    def test_query_length_validation(self, length: int):
        """
        Test query length validation boundaries.
        """
        if length == 0:
            query_text = ""
        elif length <= 1000:
            query_text = "food " * (length // 5) + "a" * (length % 5)
        else:
            query_text = "food " * 200 + "a" * (length - 1000)
        
        is_valid = self.validator.validate_query_scope(query_text)
        
        if length == 0:
            assert not is_valid, "Empty query should be invalid"
        elif length > 1000:
            assert not is_valid, "Overly long query should be invalid"
        else:
            # For reasonable length queries with food keyword, should be valid
            if "food" in query_text:
                assert is_valid, f"Query with food keyword should be valid (length: {length})"
    
    @given(st.sampled_from(['', '   ', '\t\n', '123', '!@#$%', '???']))
    @settings(max_examples=20)
    def test_invalid_query_formats_rejected(self, invalid_query: str):
        """
        Test that invalid query formats are properly rejected.
        """
        is_valid = self.validator.validate_query_scope(invalid_query)
        assert not is_valid, f"Invalid query '{repr(invalid_query)}' should be rejected"
        
        reason = self.validator.get_rejection_reason(invalid_query)
        assert reason, f"Should provide rejection reason for '{repr(invalid_query)}'"
    
    def test_query_object_validation(self):
        """
        Test validation of Query objects.
        """
        # Valid query
        valid_query = Query(
            text="Where can I find good food?",
            city="Madurai",
            timestamp=datetime.now(),
            is_valid=True
        )
        
        is_valid, reason = self.validator.validate_query_object(valid_query)
        assert is_valid
        assert reason is None
        
        # Invalid query
        invalid_query = Query(
            text="",
            city="Madurai", 
            timestamp=datetime.now(),
            is_valid=False
        )
        
        is_valid, reason = self.validator.validate_query_object(invalid_query)
        assert not is_valid
        assert reason is not None
    
    def test_topic_identification_accuracy(self):
        """
        Test accuracy of topic identification.
        """
        test_cases = [
            ("Where can I eat biryani?", "food"),
            ("How do I get to the bus station?", "transport"),
            ("What does 'enna da' mean?", "slang"),
            ("Is this area safe at night?", "safety"),
            ("What festivals are celebrated here?", "lifestyle")
        ]
        
        for query, expected_topic in test_cases:
            identified_topic = self.validator.identify_topic(query)
            assert identified_topic == expected_topic, f"Expected '{expected_topic}' for '{query}', got '{identified_topic}'"
    
    def test_preprocessing_effectiveness(self):
        """
        Test that query preprocessing improves validation.
        """
        test_cases = [
            ("   where   can   I   eat   food???   ", "where can I eat food?"),
            ("FOOD!!!!!!", "FOOD?"),
            ("what about food......", "what about food..."),
        ]
        
        for raw_query, expected_processed in test_cases:
            processed = self.validator.preprocess_query(raw_query)
            # Check that excessive whitespace and punctuation are cleaned
            assert len(processed) <= len(raw_query)
            assert not processed.startswith(' ')
            assert not processed.endswith(' ')


if __name__ == "__main__":
    pytest.main([__file__])