"""
Tests for phone number formatting.
Covers the format_phone utility and JobForm.clean_phone() integration.
"""
import pytest
from datetime import timedelta
from django.utils import timezone

from rental_scheduler.utils.phone import format_phone
from rental_scheduler.forms import JobForm


class TestFormatPhoneUtility:
    """Test the format_phone utility function."""
    
    def test_empty_string_returns_empty(self):
        """Empty string input returns empty string."""
        assert format_phone('') == ''
    
    def test_none_returns_empty(self):
        """None input returns empty string."""
        assert format_phone(None) == ''
    
    def test_ten_digits_formats_correctly(self):
        """10 digits formats as xxx-xxx-xxxx."""
        assert format_phone('5551234567') == '555-123-4567'
    
    def test_ten_digits_with_existing_format_normalizes(self):
        """Input already formatted as (xxx) xxx-xxxx normalizes to xxx-xxx-xxxx."""
        assert format_phone('(555) 123-4567') == '555-123-4567'
    
    def test_ten_digits_with_dashes_normalizes(self):
        """Input with dashes normalizes correctly."""
        assert format_phone('555-123-4567') == '555-123-4567'
    
    def test_eleven_digits_starting_with_1(self):
        """11 digits starting with 1 formats as 1-xxx-xxx-xxxx."""
        assert format_phone('15551234567') == '1-555-123-4567'
    
    def test_eleven_digits_with_spaces_and_parens(self):
        """11 digits with spaces and parens formats correctly."""
        assert format_phone('1 (555) 123-4567') == '1-555-123-4567'
    
    def test_partial_three_digits(self):
        """3 digits returns as-is (no dashes needed)."""
        assert format_phone('555') == '555'
    
    def test_partial_four_digits(self):
        """4 digits formats as xxx-x."""
        assert format_phone('5551') == '555-1'
    
    def test_partial_six_digits(self):
        """6 digits formats as xxx-xxx."""
        assert format_phone('555123') == '555-123'
    
    def test_partial_seven_digits(self):
        """7 digits formats as xxx-xxx-x."""
        assert format_phone('5551234') == '555-123-4'
    
    def test_more_than_ten_digits_truncates(self):
        """More than 10 digits (not starting with 1) truncates to 10."""
        assert format_phone('55512345678') == '555-123-4567'
    
    def test_more_than_eleven_digits_starting_with_1(self):
        """More than 11 digits starting with 1 truncates to 11."""
        assert format_phone('155512345678') == '1-555-123-4567'
    
    def test_only_non_digits_returns_empty(self):
        """String with no digits returns empty."""
        assert format_phone('no-digits-here!') == ''
    
    def test_mixed_with_letters(self):
        """Digits mixed with letters extracts digits only."""
        assert format_phone('555abc1234567') == '555-123-4567'


@pytest.mark.django_db
class TestJobFormCleanPhone:
    """Test JobForm.clean_phone() integration with format_phone."""
    
    def get_valid_form_data(self, calendar, phone=''):
        """Return valid form data with specified phone."""
        now = timezone.now()
        return {
            'calendar': calendar.id,
            'business_name': 'Test Business',
            'start_dt': now.strftime('%Y-%m-%dT%H:%M'),
            'end_dt': (now + timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M'),
            'all_day': False,
            'status': 'uncompleted',
            'phone': phone,
        }
    
    def test_form_formats_ten_digits(self, calendar):
        """Form normalizes 10 digits to xxx-xxx-xxxx."""
        data = self.get_valid_form_data(calendar, phone='5551234567')
        form = JobForm(data=data)
        assert form.is_valid(), form.errors
        assert form.cleaned_data['phone'] == '555-123-4567'
    
    def test_form_formats_eleven_digits_with_country_code(self, calendar):
        """Form normalizes 11 digits with leading 1 to 1-xxx-xxx-xxxx."""
        data = self.get_valid_form_data(calendar, phone='15551234567')
        form = JobForm(data=data)
        assert form.is_valid(), form.errors
        assert form.cleaned_data['phone'] == '1-555-123-4567'
    
    def test_form_normalizes_pasted_parens_format(self, calendar):
        """Form normalizes (xxx) xxx-xxxx to xxx-xxx-xxxx."""
        data = self.get_valid_form_data(calendar, phone='(555) 123-4567')
        form = JobForm(data=data)
        assert form.is_valid(), form.errors
        assert form.cleaned_data['phone'] == '555-123-4567'
    
    def test_form_allows_partial_phone(self, calendar):
        """Form allows partial phone without validation error."""
        data = self.get_valid_form_data(calendar, phone='5551')
        form = JobForm(data=data)
        assert form.is_valid(), form.errors
        assert form.cleaned_data['phone'] == '555-1'
    
    def test_form_allows_empty_phone(self, calendar):
        """Form allows empty phone (field is optional)."""
        data = self.get_valid_form_data(calendar, phone='')
        form = JobForm(data=data)
        assert form.is_valid(), form.errors
        assert form.cleaned_data['phone'] == ''

