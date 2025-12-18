"""
Tests for rental_scheduler.constants module.
Ensures the single source of truth for guardrails is working correctly.
"""
import pytest
from rental_scheduler.constants import (
    MIN_VALID_YEAR,
    MAX_VALID_YEAR,
    MAX_JOB_SPAN_DAYS,
    MAX_MULTI_DAY_EXPANSION_DAYS,
    WARN_DAYS_IN_FUTURE,
    WARN_JOB_SPAN_DAYS,
    get_guardrails_for_frontend,
)


class TestConstants:
    """Test that constants are defined with expected values."""
    
    def test_min_valid_year_is_reasonable(self):
        """MIN_VALID_YEAR should be a reasonable year in the past."""
        assert MIN_VALID_YEAR == 2000
        assert isinstance(MIN_VALID_YEAR, int)
    
    def test_max_valid_year_is_reasonable(self):
        """MAX_VALID_YEAR should be a reasonable year in the future."""
        assert MAX_VALID_YEAR == 2100
        assert isinstance(MAX_VALID_YEAR, int)
    
    def test_max_job_span_days(self):
        """MAX_JOB_SPAN_DAYS should be set."""
        assert MAX_JOB_SPAN_DAYS == 365
        assert isinstance(MAX_JOB_SPAN_DAYS, int)
    
    def test_max_multi_day_expansion_days(self):
        """MAX_MULTI_DAY_EXPANSION_DAYS should be set for API safety."""
        assert MAX_MULTI_DAY_EXPANSION_DAYS == 120
        assert isinstance(MAX_MULTI_DAY_EXPANSION_DAYS, int)
    
    def test_warn_days_in_future(self):
        """WARN_DAYS_IN_FUTURE should be set for UX warnings (3 years)."""
        assert WARN_DAYS_IN_FUTURE == 1095
        assert isinstance(WARN_DAYS_IN_FUTURE, int)
    
    def test_warn_job_span_days(self):
        """WARN_JOB_SPAN_DAYS should be less than or equal to MAX_JOB_SPAN_DAYS."""
        assert WARN_JOB_SPAN_DAYS == 60
        assert WARN_JOB_SPAN_DAYS <= MAX_JOB_SPAN_DAYS


class TestGetGuardrailsForFrontend:
    """Test the helper function that provides guardrails to frontend."""
    
    def test_returns_dict(self):
        """Should return a dictionary."""
        result = get_guardrails_for_frontend()
        assert isinstance(result, dict)
    
    def test_contains_expected_keys(self):
        """Should contain all expected camelCase keys."""
        result = get_guardrails_for_frontend()
        expected_keys = {
            'minValidYear',
            'maxValidYear',
            'maxJobSpanDays',
            'warnDaysInFuture',
            'warnJobSpanDays',
        }
        assert set(result.keys()) == expected_keys
    
    def test_values_match_constants(self):
        """Values should match the corresponding constants."""
        result = get_guardrails_for_frontend()
        assert result['minValidYear'] == MIN_VALID_YEAR
        assert result['maxValidYear'] == MAX_VALID_YEAR
        assert result['maxJobSpanDays'] == MAX_JOB_SPAN_DAYS
        assert result['warnDaysInFuture'] == WARN_DAYS_IN_FUTURE
        assert result['warnJobSpanDays'] == WARN_JOB_SPAN_DAYS
    
    def test_is_json_serializable(self):
        """Result should be JSON serializable."""
        import json
        result = get_guardrails_for_frontend()
        # Should not raise
        json_str = json.dumps(result)
        assert json_str
        # Should round-trip
        parsed = json.loads(json_str)
        assert parsed == result

