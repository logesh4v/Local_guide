"""
Property-based tests for guard agent validation.
**Feature: local-guide-ai, Property 5: Guard agent validation**
**Validates: Requirements 3.3, 3.4**
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.guard_agent import GuardAgent
from models import Response


class TestGuardValidationProperty:
    """Property-based tests for guard agent validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.guard = GuardAgent()
        
        # Sample context for testing
        self.sample_context = """# Test City Context
        Famous for local temple and traditional food.
        Popular dishes include biryani, idli, and dosa.
        Local transport includes buses and auto rickshaws.
        Traditional festivals are celebrated with enthusiasm.
        Shopping areas include main market and commercial street.
        """
    
    @given(st.sampled_from([
        "This isn't covered in my local context.",
        "I don't have enough local data to answer that.",
        "My knowledge is limited to what's in the context file."
    ]))
    @settings(max_examples=100)
    def test_standardized_refusals_always_valid(self, refusal_text: str):
        """
        **Feature: local-guide-ai, Property 5: Guard agent validation**
        For any standardized refusal response, the Guard Agent should validate 
        it as acceptable regardless of context.
        """
        # Standardized refusals should always be valid
        assert self.guard.validate_response(refusal_text, self.sample_context)
        assert not self.guard.detect_hallucination(refusal_text, self.sample_context)
        
        # Should work even with empty context
        assert self.guard.validate_response(refusal_text, "")
        assert self.guard.validate_response(refusal_text, None)
    
    @given(st.text(min_size=10, max_size=200))
    @settings(max_examples=100)
    def test_context_based_responses_validation(self, response_text: str):
        """
        **Feature: local-guide-ai, Property 5: Guard agent validation**
        For any generated response, the Guard Agent should validate that no 
        information outside the context file is included.
        """
        assume(response_text.strip())  # Skip empty responses
        assume(not any(phrase in response_text for phrase in self.guard.standardized_refusals))  # Skip refusals
        
        # Create a response that contains context words
        context_words = ['temple', 'biryani', 'idli', 'buses', 'festival', 'market']
        context_based_response = f"{response_text} The local temple and biryani are famous here."
        
        # Response with context words should be more likely to validate
        validation_result = self.guard.validate_response(context_based_response, self.sample_context)
        
        # If validation fails, it should be due to suspicious patterns or insufficient overlap
        if not validation_result:
            details = self.guard.get_validation_details(context_based_response, self.sample_context)
            # Should fail for legitimate reasons
            assert (details['has_suspicious_patterns'] or 
                   details['overlap_ratio'] < 0.3 or 
                   details['external_word_count'] > details['response_word_count'] * 0.4)
    
    @given(st.sampled_from([
        "According to Wikipedia, this city is famous.",
        "Research shows that this area is popular.",
        "I think this place is good for tourists.",
        "Generally speaking, this is a nice location.",
        "Modern studies indicate high visitor satisfaction.",
        "Experts say this is the best restaurant worldwide."
    ]))
    @settings(max_examples=50)
    def test_suspicious_patterns_detected(self, suspicious_response: str):
        """
        Test that responses with suspicious patterns are flagged.
        """
        # Responses with suspicious patterns should be flagged
        assert self.guard.detect_hallucination(suspicious_response, self.sample_context)
        assert not self.guard.validate_response(suspicious_response, self.sample_context)
        
        # Should be corrected to refusal
        corrected, was_corrected = self.guard.validate_and_correct_response(
            suspicious_response, self.sample_context
        )
        assert was_corrected
        assert corrected in self.guard.standardized_refusals
    
    @given(st.text(min_size=20, max_size=100))
    @settings(max_examples=50)
    def test_external_knowledge_detection(self, base_text: str):
        """
        Test detection of external knowledge not present in context.
        """
        assume(base_text.strip())
        
        # Create response with external knowledge
        external_response = f"{base_text} This information comes from government statistics and official reports."
        
        # Should detect external knowledge
        contains_external = self.guard._contains_external_knowledge(external_response, self.sample_context)
        
        # If external knowledge detected, validation should fail
        if contains_external:
            assert self.guard.detect_hallucination(external_response, self.sample_context)
    
    @given(st.floats(min_value=0.0, max_value=1.0))
    @settings(max_examples=50)
    def test_context_overlap_threshold(self, overlap_ratio: float):
        """
        Test context overlap validation with different ratios.
        """
        # Create response with controlled overlap
        context_words = ['temple', 'biryani', 'idli', 'buses', 'festival']
        
        if overlap_ratio >= 0.3:
            # High overlap - use mostly context words
            response_words = context_words[:int(len(context_words) * overlap_ratio)]
            response = " ".join(response_words) + " are popular here."
            
            # Should have sufficient overlap
            assert self.guard._has_sufficient_context_overlap(response, self.sample_context)
        else:
            # Low overlap - use mostly non-context words
            non_context_words = ['quantum', 'physics', 'molecular', 'algorithm', 'cryptocurrency']
            response = " ".join(non_context_words) + " temple"  # Add one context word
            
            # Should have insufficient overlap
            assert not self.guard._has_sufficient_context_overlap(response, self.sample_context, min_overlap=0.3)
    
    def test_response_object_validation(self):
        """
        Test validation of Response objects.
        """
        # Valid response object
        valid_response = Response(
            text="The local temple and biryani are famous attractions here.",
            is_refusal=False,
            source_context="test context"
        )
        
        validated = self.guard.validate_response_object(valid_response, self.sample_context)
        assert validated.validation_passed
        assert validated.text == valid_response.text
        
        # Invalid response object (should be corrected)
        invalid_response = Response(
            text="According to Wikipedia, this city has modern infrastructure.",
            is_refusal=False,
            source_context="test context"
        )
        
        validated = self.guard.validate_response_object(invalid_response, self.sample_context)
        assert not validated.validation_passed
        assert validated.is_refusal
        assert validated.text in self.guard.standardized_refusals
    
    def test_batch_validation(self):
        """
        Test batch validation of multiple responses.
        """
        responses = [
            "The temple here is very famous.",  # Should be valid
            "According to research, this is popular.",  # Should be invalid
            "This isn't covered in my local context.",  # Should be valid (refusal)
            "Biryani and idli are local specialties."  # Should be valid
        ]
        
        results = self.guard.batch_validate_responses(responses, self.sample_context)
        
        assert len(results) == 4
        assert results[0][1] is True   # Temple response valid
        assert results[1][1] is False  # Research response invalid
        assert results[2][1] is True   # Refusal valid
        assert results[3][1] is True   # Food response valid
    
    def test_validation_details(self):
        """
        Test detailed validation information.
        """
        response = "The local temple and biryani are famous here."
        details = self.guard.get_validation_details(response, self.sample_context)
        
        assert 'is_valid' in details
        assert 'overlap_ratio' in details
        assert 'response_word_count' in details
        assert 'external_words' in details
        assert 'overlap_words' in details
        
        # Should have good overlap with context
        assert details['overlap_ratio'] > 0
        assert details['response_word_count'] > 0
    
    def test_force_refusal_reasons(self):
        """
        Test that appropriate refusals are returned based on reasons.
        """
        context_refusal = self.guard.force_refusal("context issue")
        assert context_refusal == "This isn't covered in my local context."
        
        data_refusal = self.guard.force_refusal("insufficient data")
        assert data_refusal == "I don't have enough local data to answer that."
        
        general_refusal = self.guard.force_refusal("other issue")
        assert general_refusal == "My knowledge is limited to what's in the context file."
    
    def test_content_word_extraction(self):
        """
        Test extraction of content words from text.
        """
        text = "The famous temple and delicious biryani are very popular here."
        content_words = self.guard._extract_content_words(text)
        
        # Should contain content words but not common words
        assert 'temple' in content_words
        assert 'biryani' in content_words
        assert 'the' not in content_words
        assert 'and' not in content_words
        assert 'are' not in content_words
    
    def test_empty_input_handling(self):
        """
        Test handling of empty or None inputs.
        """
        # Empty response
        assert not self.guard.validate_response("", self.sample_context)
        assert not self.guard.validate_response(None, self.sample_context)
        
        # Empty context
        assert not self.guard.validate_response("Some response", "")
        assert not self.guard.validate_response("Some response", None)
        
        # Both empty
        assert not self.guard.validate_response("", "")
    
    def test_refusal_statistics(self):
        """
        Test refusal statistics calculation.
        """
        responses = [
            "This isn't covered in my local context.",
            "The temple is famous here.",
            "I don't have enough local data to answer that.",
            "Biryani is a specialty.",
            "My knowledge is limited to what's in the context file."
        ]
        
        stats = self.guard.get_refusal_statistics(responses)
        
        assert stats['total_responses'] == 5
        assert stats['refusal_count'] == 3
        assert stats['refusal_rate'] == 0.6
        assert len(stats['refusal_breakdown']) == 3


if __name__ == "__main__":
    pytest.main([__file__])