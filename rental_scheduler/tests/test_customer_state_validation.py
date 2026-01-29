"""
Tests for customer state code normalization and validation.
"""
import pytest
from django.core.exceptions import ValidationError

from rental_scheduler.views import _normalize_state_code


class TestNormalizeStateCode:
    """Test the _normalize_state_code helper function."""

    def test_accepts_lowercase_code(self):
        """Should normalize lowercase 2-letter codes to uppercase."""
        assert _normalize_state_code("tn") == "TN"
        assert _normalize_state_code("ky") == "KY"
        assert _normalize_state_code("ca") == "CA"

    def test_accepts_uppercase_code(self):
        """Should accept already-uppercase 2-letter codes."""
        assert _normalize_state_code("TN") == "TN"
        assert _normalize_state_code("KY") == "KY"
        assert _normalize_state_code("NY") == "NY"

    def test_accepts_blank(self):
        """Should return empty string for blank/None input."""
        assert _normalize_state_code("") == ""
        assert _normalize_state_code("  ") == ""
        assert _normalize_state_code(None) == ""

    def test_accepts_territory_codes(self):
        """Should accept US territory codes."""
        assert _normalize_state_code("PR") == "PR"
        assert _normalize_state_code("GU") == "GU"
        assert _normalize_state_code("VI") == "VI"
        assert _normalize_state_code("AS") == "AS"
        assert _normalize_state_code("MP") == "MP"

    def test_accepts_dc(self):
        """Should accept District of Columbia."""
        assert _normalize_state_code("DC") == "DC"
        assert _normalize_state_code("dc") == "DC"

    def test_accepts_full_state_names(self):
        """Should defensively map full state names to codes."""
        assert _normalize_state_code("Tennessee") == "TN"
        assert _normalize_state_code("TENNESSEE") == "TN"
        assert _normalize_state_code("Kentucky") == "KY"
        assert _normalize_state_code("Puerto Rico") == "PR"

    def test_trims_whitespace(self):
        """Should trim leading/trailing whitespace."""
        assert _normalize_state_code("  TN  ") == "TN"
        assert _normalize_state_code(" Tennessee ") == "TN"

    def test_rejects_invalid_code(self):
        """Should raise ValidationError for invalid 2-letter codes."""
        with pytest.raises(ValidationError, match="State must be a valid 2-letter USPS code"):
            _normalize_state_code("XX")

    def test_rejects_invalid_name(self):
        """Should raise ValidationError for unrecognized state names."""
        with pytest.raises(ValidationError, match="State must be a valid 2-letter USPS code"):
            _normalize_state_code("Fake State")

    def test_rejects_random_input(self):
        """Should raise ValidationError for random non-state input."""
        with pytest.raises(ValidationError):
            _normalize_state_code("12345")
        with pytest.raises(ValidationError):
            _normalize_state_code("ABC")
