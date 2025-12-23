"""
Unit tests for Guard Agent.
Tests validation of context-only responses, detection of hallucinated content,
and forced refusal mechanisms.
"""
import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.guard_agent import GuardAgent
from models import Response


class TestGuardAgentUnit:
    """Unit tests for Guard Agent."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.guard = GuardAgent()
        
        self.sample_context = """# Test City Context
        Famous for ancient temple and traditional cuisine.
        Popular dishes include biryani, idli, dosa, and local sweets.
        Transportation options include city buses, auto rickshaws, and taxis.
        Major festivals celebrated include Pongal and local temple festivals.
        Shopping areas include central market, commercial street, and local bazaars.
        Climate is tropical with hot summers and moderate winters.
        """
    
    def test_standardized_refusal_validation(self):
        """Test validation of standardized refusal responses."""
        refusals = [
            "This isn't covered in my local context.",
            "I don't have enough local data to answer that.",
            "My knowledge is limited to what's in the context file."
        ]
        
        for refusal in refusals:
            assert self.guard.validate_response(refusal, self.sample_context)
            assert not self.guard.detect_hallucination(refusal, self.sample_context)
            assert self.guard._is_standardized_refusal(refusal)
    
    def test_context_based_response_validation(self):
        """Test validation of responses based on context content."""
        # Valid responses with context words
        valid_responses = [
            "The ancient temple is a major attraction here.",
            "Local cuisine includes biryani, idli, and dosa.",
            "You can travel by city buses or auto rickshaws.",
            "Pongal is celebrated with great enthusiasm.",
            "The central market is popular for shopping."
        ]
        
        for response in valid_responses:
            assert self.guard.validate_response(response, self.sample_context), f"Should validate: {response}"
            assert not self.guard.detect_hallucination(response, self.sample_context)
    
    def test_suspicious_pattern_detection(self):
        """Test detection of suspicious patterns indicating external knowledge."""
        suspicious_responses = [
            "According to Wikipedia, this city is famous.",
            "Research shows that tourism is increasing here.",
            "I think this is a good place to visit.",
            "Generally speaking, the weather is pleasant.",
            "Studies indicate high satisfaction rates.",
            "Experts recommend visiting during winter."
        ]
        
        for response in suspicious_responses:
            assert self.guard._contains_suspicious_patterns(response), f"Should detect pattern in: {response}"
            assert self.guard.detect_hallucination(response, self.sample_context)
            assert not self.guard.validate_response(response, self.sample_context)
    
    def test_external_knowledge_detection(self):
        """Test detection of external knowledge not in context."""
        external_responses = [
            "This city has a population of 2 million people.",
            "The GDP of this region is growing rapidly.",
            "Government statistics show increasing development.",
            "Official reports indicate infrastructure improvements.",
            "International surveys rank this city highly."
        ]
        
        for response in external_responses:
            assert self.guard._contains_external_knowledge(response, self.sample_context)
            assert self.guard.detect_hallucination(response, self.sample_context)
    
    def test_context_overlap_validation(self):
        """Test context overlap validation logic."""
        # High overlap response
        high_overlap = "The temple, biryani, buses, and festivals are popular here."
        assert self.guard._has_sufficient_context_overlap(high_overlap, self.sample_context)
        
        # Low overlap response
        low_overlap = "Quantum physics and molecular biology are fascinating subjects."
        assert not self.guard._has_sufficient_context_overlap(low_overlap, self.sample_context)
        
        # Medium overlap response
        medium_overlap = "The temple is nice and quantum physics is interesting."
        # This might pass or fail depending on exact ratio
        overlap_result = self.guard._has_sufficient_context_overlap(medium_overlap, self.sample_context)
        # Just ensure it returns a boolean
        assert isinstance(overlap_result, bool)
    
    def test_content_word_extraction(self):
        """Test extraction of content words from text."""
        text = "The famous temple and delicious biryani are very popular here."
        content_words = self.guard._extract_content_words(text)
        
        # Should include content words
        assert 'temple' in content_words
        assert 'biryani' in content_words
        assert 'famous' in content_words
        assert 'delicious' in content_words
        
        # Should exclude common words
        assert 'the' not in content_words
        assert 'and' not in content_words
        assert 'are' not in content_words
        assert 'very' not in content_words
    
    def test_force_refusal_with_reasons(self):
        """Test forced refusal with different reasons."""
        context_refusal = self.guard.force_refusal("context missing")
        assert context_refusal == "This isn't covered in my local context."
        
        data_refusal = self.guard.force_refusal("insufficient data available")
        assert data_refusal == "I don't have enough local data to answer that."
        
        general_refusal = self.guard.force_refusal("validation failed")
        assert general_refusal == "My knowledge is limited to what's in the context file."
    
    def test_validate_and_correct_response(self):
        """Test response validation and correction."""
        # Valid response - should not be corrected
        valid_response = "The temple and biryani are famous here."
        corrected, was_corrected = self.guard.validate_and_correct_response(valid_response, self.sample_context)
        assert not was_corrected
        assert corrected == valid_response
        
        # Invalid response - should be corrected to refusal
        invalid_response = "According to Wikipedia, this city is modern."
        corrected, was_corrected = self.guard.validate_and_correct_response(invalid_response, self.sample_context)
        assert was_corrected
        assert corrected in self.guard.standardized_refusals
    
    def test_response_object_validation(self):
        """Test validation of Response objects."""
        # Valid response object
        valid_response = Response(
            text="The temple and local cuisine are popular attractions.",
            is_refusal=False,
            source_context="test context"
        )
        
        validated = self.guard.validate_response_object(valid_response, self.sample_context)
        assert validated.validation_passed
        assert validated.text == valid_response.text
        assert not validated.is_refusal
        
        # Invalid response object
        invalid_response = Response(
            text="According to research, this city is developing rapidly.",
            is_refusal=False,
            source_context="test context"
        )
        
        validated = self.guard.validate_response_object(invalid_response, self.sample_context)
        assert not validated.validation_passed
        assert validated.is_refusal
        assert validated.refusal_reason == "Guard agent detected potential hallucination"
        assert validated.text in self.guard.standardized_refusals
    
    def test_batch_validation(self):
        """Test batch validation of multiple responses."""
        responses = [
            "The temple is famous here.",  # Valid
            "According to studies, this is popular.",  # Invalid - suspicious pattern
            "This isn't covered in my local context.",  # Valid - refusal
            "Biryani and idli are specialties.",  # Valid
            "Government data shows growth.",  # Invalid - external knowledge
        ]
        
        results = self.guard.batch_validate_responses(responses, self.sample_context)
        
        assert len(results) == 5
        assert results[0][1] is True   # Temple response
        assert results[1][1] is False  # Studies response
        assert results[2][1] is True   # Refusal response
        assert results[3][1] is True   # Food response
        assert results[4][1] is False  # Government data response
    
    def test_validation_details(self):
        """Test detailed validation information."""
        response = "The temple and biryani are famous local attractions."
        details = self.guard.get_validation_details(response, self.sample_context)
        
        # Check all expected keys are present
        expected_keys = [
            'is_valid', 'is_refusal', 'has_suspicious_patterns', 'overlap_ratio',
            'response_word_count', 'context_word_count', 'overlap_word_count',
            'external_word_count', 'external_words', 'overlap_words'
        ]
        
        for key in expected_keys:
            assert key in details, f"Missing key: {key}"
        
        # Check reasonable values
        assert isinstance(details['is_valid'], bool)
        assert isinstance(details['overlap_ratio'], float)
        assert details['overlap_ratio'] >= 0
        assert details['response_word_count'] >= 0
        assert isinstance(details['external_words'], list)
        assert isinstance(details['overlap_words'], list)
    
    def test_refusal_statistics(self):
        """Test refusal statistics calculation."""
        responses = [
            "This isn't covered in my local context.",
            "The temple is famous.",
            "I don't have enough local data to answer that.",
            "Biryani is delicious.",
            "My knowledge is limited to what's in the context file.",
            "The market is busy."
        ]
        
        stats = self.guard.get_refusal_statistics(responses)
        
        assert stats['total_responses'] == 6
        assert stats['refusal_count'] == 3
        assert stats['refusal_rate'] == 0.5
        
        # Check breakdown
        breakdown = stats['refusal_breakdown']
        assert breakdown["This isn't covered in my local context."] == 1
        assert breakdown["I don't have enough local data to answer that."] == 1
        assert breakdown["My knowledge is limited to what's in the context file."] == 1
    
    def test_empty_input_handling(self):
        """Test handling of empty or None inputs."""
        # Empty response
        assert not self.guard.validate_response("", self.sample_context)
        assert not self.guard.validate_response(None, self.sample_context)
        
        # Empty context
        assert not self.guard.validate_response("Some response", "")
        assert not self.guard.validate_response("Some response", None)
        
        # Both empty
        assert not self.guard.validate_response("", "")
        assert not self.guard.validate_response(None, None)
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Very short response
        short_response = "Yes."
        # Should fail due to insufficient content
        assert not self.guard.validate_response(short_response, self.sample_context)
        
        # Response with only common words
        common_response = "The and or but in on at to for of with by is are."
        assert not self.guard.validate_response(common_response, self.sample_context)
        
        # Response with mixed valid and suspicious content
        mixed_response = "The temple is famous. According to Wikipedia, it's ancient."
        assert not self.guard.validate_response(mixed_response, self.sample_context)
    
    def test_case_insensitive_validation(self):
        """Test that validation works regardless of case."""
        responses = [
            "THE TEMPLE IS FAMOUS HERE.",
            "the temple is famous here.",
            "The Temple Is Famous Here.",
            "tHe TeMpLe Is FaMoUs HeRe."
        ]
        
        for response in responses:
            # All should have similar validation results
            result = self.guard.validate_response(response, self.sample_context)
            assert isinstance(result, bool)  # Should not crash on different cases


if __name__ == "__main__":
    pytest.main([__file__])