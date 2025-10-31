"""
Unit tests for the rental_scheduler app, focusing on event datetime normalization.
"""

from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta
from rental_scheduler.utils.events import normalize_event_datetimes


class EventDatetimeNormalizationTests(TestCase):
    """Tests for the normalize_event_datetimes function"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Get the local timezone for testing
        self.local_tz = timezone.get_current_timezone()
    
    def test_all_day_single_day_event(self):
        """Test all-day event for a single day (e.g., Oct 16)"""
        # Input: Oct 16 as date string
        start_value = "2025-10-16"
        end_value = "2025-10-16"
        
        start_dt, end_dt, start_json, end_json, all_day = normalize_event_datetimes(
            start_value, end_value, all_day=True
        )
        
        # Verify stored datetimes are at midnight local time, converted to UTC
        start_local = timezone.localtime(start_dt, self.local_tz)
        self.assertEqual(start_local.hour, 0)
        self.assertEqual(start_local.minute, 0)
        self.assertEqual(start_local.date().isoformat(), "2025-10-16")
        
        # Verify end is next day (exclusive)
        end_local = timezone.localtime(end_dt, self.local_tz)
        self.assertEqual(end_local.date().isoformat(), "2025-10-17")
        
        # Verify JSON output is date-only strings
        self.assertEqual(start_json, "2025-10-16")
        self.assertEqual(end_json, "2025-10-17")  # Exclusive
        self.assertTrue(all_day)
    
    def test_all_day_multi_day_event(self):
        """Test all-day event spanning multiple days (e.g., Oct 16-17)"""
        # Input: Oct 16-17 (inclusive in UI, should become Oct 16-18 exclusive)
        start_value = "2025-10-16"
        end_value = "2025-10-17"
        
        start_dt, end_dt, start_json, end_json, all_day = normalize_event_datetimes(
            start_value, end_value, all_day=True
        )
        
        # Verify dates
        start_local = timezone.localtime(start_dt, self.local_tz)
        end_local = timezone.localtime(end_dt, self.local_tz)
        
        self.assertEqual(start_local.date().isoformat(), "2025-10-16")
        self.assertEqual(end_local.date().isoformat(), "2025-10-18")  # Exclusive
        
        # Verify JSON output
        self.assertEqual(start_json, "2025-10-16")
        self.assertEqual(end_json, "2025-10-18")  # Exclusive
        self.assertTrue(all_day)
    
    def test_all_day_with_iso_datetime_input(self):
        """Test all-day event with ISO datetime string input (time should be ignored)"""
        # Input with time component (should be ignored for all-day)
        start_value = "2025-10-16T14:30:00"
        end_value = "2025-10-16T15:30:00"
        
        start_dt, end_dt, start_json, end_json, all_day = normalize_event_datetimes(
            start_value, end_value, all_day=True
        )
        
        # Verify time is normalized to midnight
        start_local = timezone.localtime(start_dt, self.local_tz)
        self.assertEqual(start_local.hour, 0)
        self.assertEqual(start_local.minute, 0)
        self.assertEqual(start_local.date().isoformat(), "2025-10-16")
        
        # Verify end is next day (exclusive, single-day event)
        end_local = timezone.localtime(end_dt, self.local_tz)
        self.assertEqual(end_local.date().isoformat(), "2025-10-17")
        
        # Verify JSON output
        self.assertEqual(start_json, "2025-10-16")
        self.assertEqual(end_json, "2025-10-17")
        self.assertTrue(all_day)
    
    def test_all_day_no_end_date(self):
        """Test all-day event with no end date (should default to next day)"""
        start_value = "2025-10-16"
        end_value = None
        
        start_dt, end_dt, start_json, end_json, all_day = normalize_event_datetimes(
            start_value, end_value, all_day=True
        )
        
        # Verify dates
        start_local = timezone.localtime(start_dt, self.local_tz)
        end_local = timezone.localtime(end_dt, self.local_tz)
        
        self.assertEqual(start_local.date().isoformat(), "2025-10-16")
        self.assertEqual(end_local.date().isoformat(), "2025-10-17")  # Next day
        
        # Verify JSON output
        self.assertEqual(start_json, "2025-10-16")
        self.assertEqual(end_json, "2025-10-17")
        self.assertTrue(all_day)
    
    def test_timed_event_with_iso_strings(self):
        """Test timed event with ISO datetime strings"""
        # Oct 14, 9:00 AM - 11:00 AM
        start_value = "2025-10-14T09:00:00"
        end_value = "2025-10-14T11:00:00"
        
        start_dt, end_dt, start_json, end_json, all_day = normalize_event_datetimes(
            start_value, end_value, all_day=False
        )
        
        # Verify datetimes are preserved (with timezone)
        start_local = timezone.localtime(start_dt, self.local_tz)
        end_local = timezone.localtime(end_dt, self.local_tz)
        
        self.assertEqual(start_local.hour, 9)
        self.assertEqual(start_local.minute, 0)
        self.assertEqual(end_local.hour, 11)
        self.assertEqual(end_local.minute, 0)
        
        # Verify JSON output includes time
        self.assertIn("T", start_json)
        self.assertIn("T", end_json)
        self.assertIn("09:00:00", start_json)
        self.assertIn("11:00:00", end_json)
        self.assertFalse(all_day)
    
    def test_timed_event_with_timezone_aware_datetime(self):
        """Test timed event with timezone-aware datetime objects"""
        # Create timezone-aware datetimes
        naive_start = datetime(2025, 10, 14, 9, 0, 0)
        naive_end = datetime(2025, 10, 14, 11, 0, 0)
        start_value = timezone.make_aware(naive_start, self.local_tz)
        end_value = timezone.make_aware(naive_end, self.local_tz)
        
        start_dt, end_dt, start_json, end_json, all_day = normalize_event_datetimes(
            start_value, end_value, all_day=False
        )
        
        # Verify datetimes are preserved
        start_local = timezone.localtime(start_dt, self.local_tz)
        end_local = timezone.localtime(end_dt, self.local_tz)
        
        self.assertEqual(start_local.hour, 9)
        self.assertEqual(start_local.minute, 0)
        self.assertEqual(end_local.hour, 11)
        self.assertEqual(end_local.minute, 0)
        
        # Verify JSON output includes time
        self.assertIn("T", start_json)
        self.assertIn("T", end_json)
        self.assertFalse(all_day)
    
    def test_timed_event_no_end_date(self):
        """Test timed event with no end date (should use start as end)"""
        start_value = "2025-10-14T09:00:00"
        end_value = None
        
        start_dt, end_dt, start_json, end_json, all_day = normalize_event_datetimes(
            start_value, end_value, all_day=False
        )
        
        # Verify end equals start
        self.assertEqual(start_dt, end_dt)
        self.assertEqual(start_json, end_json)
        self.assertFalse(all_day)
    
    def test_all_day_stored_as_utc(self):
        """Test that all-day events are stored in UTC in database"""
        start_value = "2025-10-16"
        end_value = "2025-10-16"
        
        start_dt, end_dt, _, _, _ = normalize_event_datetimes(
            start_value, end_value, all_day=True
        )
        
        # Verify stored datetimes are in UTC
        from datetime import timezone as dt_timezone
        self.assertEqual(start_dt.tzinfo, dt_timezone.utc)
        self.assertEqual(end_dt.tzinfo, dt_timezone.utc)
    
    def test_timed_event_stored_as_utc(self):
        """Test that timed events are stored in UTC in database"""
        start_value = "2025-10-14T09:00:00"
        end_value = "2025-10-14T11:00:00"
        
        start_dt, end_dt, _, _, _ = normalize_event_datetimes(
            start_value, end_value, all_day=False
        )
        
        # Verify stored datetimes are in UTC
        from datetime import timezone as dt_timezone
        self.assertEqual(start_dt.tzinfo, dt_timezone.utc)
        self.assertEqual(end_dt.tzinfo, dt_timezone.utc)
    
    def test_all_day_exclusive_end_semantics(self):
        """Test that all-day events use exclusive end date semantics"""
        # A 3-day event: Oct 16, 17, 18 (inclusive)
        # Should be stored as Oct 16 - Oct 19 (exclusive)
        start_value = "2025-10-16"
        end_value = "2025-10-18"  # Inclusive last day
        
        start_dt, end_dt, start_json, end_json, all_day = normalize_event_datetimes(
            start_value, end_value, all_day=True
        )
        
        # Verify exclusive end
        self.assertEqual(start_json, "2025-10-16")
        self.assertEqual(end_json, "2025-10-19")  # Exclusive (one day after last visible day)
        
        # Verify the duration is correct (3 days)
        start_local = timezone.localtime(start_dt, self.local_tz).date()
        end_local = timezone.localtime(end_dt, self.local_tz).date()
        duration = (end_local - start_local).days
        self.assertEqual(duration, 3)


class EventDatetimeEdgeCaseTests(TestCase):
    """Edge case tests for event datetime normalization"""
    
    def test_all_day_event_at_year_boundary(self):
        """Test all-day event at year boundary (Dec 31 - Jan 1)"""
        start_value = "2025-12-31"
        end_value = "2026-01-01"
        
        start_dt, end_dt, start_json, end_json, all_day = normalize_event_datetimes(
            start_value, end_value, all_day=True
        )
        
        # Verify dates span year boundary correctly
        self.assertEqual(start_json, "2025-12-31")
        self.assertEqual(end_json, "2026-01-02")  # Exclusive
        self.assertTrue(all_day)
    
    def test_all_day_event_in_dst_transition(self):
        """Test all-day event during DST transition"""
        # Spring forward or fall back - event should still be normalized to midnight
        # Using a date known to be in DST transition for US timezones
        start_value = "2025-03-09"  # DST starts in US
        end_value = "2025-03-09"
        
        start_dt, end_dt, start_json, end_json, all_day = normalize_event_datetimes(
            start_value, end_value, all_day=True
        )
        
        # Verify midnight is maintained despite DST
        local_tz = timezone.get_current_timezone()
        start_local = timezone.localtime(start_dt, local_tz)
        self.assertEqual(start_local.hour, 0)
        self.assertEqual(start_local.minute, 0)
        
        # Verify JSON output
        self.assertEqual(start_json, "2025-03-09")
        self.assertEqual(end_json, "2025-03-10")
        self.assertTrue(all_day)

