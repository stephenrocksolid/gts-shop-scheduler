"""
Unit tests for the RentalCalculator service.
Tests all calculation logic to ensure accuracy and consistency.
"""
import unittest
import tempfile
import os
from datetime import datetime, timedelta
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone

from rental_scheduler.models import Trailer, TrailerCategory, SystemSettings
from rental_scheduler.services.rental_calculator import RentalCalculator


class RentalCalculatorTestCase(TestCase):
    """Test cases for RentalCalculator service"""
    
    def setUp(self):
        """Set up test data"""
        # Create test category
        self.category = TrailerCategory.objects.create(category="Test Category")
        
        # Create test trailer
        self.trailer = Trailer.objects.create(
            category=self.category,
            number="TEST001",
            model="Test Trailer",
            hauling_capacity=Decimal('2000.00'),
            half_day_rate=Decimal('50.00'),
            daily_rate=Decimal('75.00'),
            weekly_rate=Decimal('300.00'),
            width=Decimal('5.00'),
            length=Decimal('10.00')
        )
        
        # Create a temporary directory for test license scan path
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test system settings with valid path
        self.settings = SystemSettings.objects.create(
            winch_price=Decimal('25.00'),
            hitch_bar_price=Decimal('15.00'),
            furniture_blanket_price=Decimal('5.00'),
            strap_chain_price=Decimal('3.00'),
            evening_pickup_price=Decimal('50.00'),
            tax_rate=Decimal('8.25'),
            license_scan_path=self.temp_dir
        )
        
        # Base datetime for consistent testing
        self.base_datetime = timezone.make_aware(datetime(2024, 1, 15, 7, 0, 0))
    
    def tearDown(self):
        """Clean up test data"""
        # Remove temporary directory
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_calculation_constants(self):
        """Test that calculation constants are correctly defined"""
        self.assertEqual(RentalCalculator.HALF_DAY_HOURS, 5)
        self.assertEqual(RentalCalculator.HALF_DAY_THRESHOLD, Decimal('5') / Decimal('24'))
        self.assertEqual(RentalCalculator.DAILY_RATE_MAX_DAYS, 4)
        self.assertEqual(RentalCalculator.WEEKLY_RATE_MAX_DAYS, 7)
        self.assertEqual(RentalCalculator.WEEKLY_RATE_DIVISOR, 6)
    
    def test_calculate_duration_info_half_day(self):
        """Test duration calculation for half day rental (5 hours)"""
        start = self.base_datetime
        end = start + timedelta(hours=5)
        
        result = RentalCalculator.calculate_duration_info(start, end)
        
        self.assertEqual(result['hours'], 5.0)
        self.assertEqual(result['days'], 5.0/24)  # 0.208333...
        self.assertTrue(result['is_half_day'])
        self.assertEqual(result['rate_category'], 'half_day')
        self.assertEqual(result['days_display'], '5 hours')
    
    def test_calculate_duration_info_half_day_edge(self):
        """Test duration calculation at the edge of half day (5 hours exactly)"""
        start = self.base_datetime
        end = start + timedelta(hours=5, seconds=0)
        
        result = RentalCalculator.calculate_duration_info(start, end)
        
        self.assertTrue(result['is_half_day'])
        self.assertEqual(result['rate_category'], 'half_day')
    
    def test_calculate_duration_info_just_over_half_day(self):
        """Test duration calculation just over half day (5 hours 1 minute)"""
        start = self.base_datetime
        end = start + timedelta(hours=5, minutes=1)
        
        result = RentalCalculator.calculate_duration_info(start, end)
        
        self.assertFalse(result['is_half_day'])
        self.assertEqual(result['rate_category'], 'daily')
    
    def test_calculate_duration_info_daily(self):
        """Test duration calculation for daily rental (2 days)"""
        start = self.base_datetime
        end = start + timedelta(days=2)
        
        result = RentalCalculator.calculate_duration_info(start, end)
        
        self.assertEqual(result['days'], 2.0)
        self.assertFalse(result['is_half_day'])
        self.assertEqual(result['rate_category'], 'daily')
        self.assertEqual(result['days_display'], '2 days')
    
    def test_calculate_duration_info_weekly(self):
        """Test duration calculation for weekly rental (6 days)"""
        start = self.base_datetime
        end = start + timedelta(days=6)
        
        result = RentalCalculator.calculate_duration_info(start, end)
        
        self.assertEqual(result['days'], 6.0)
        self.assertEqual(result['rate_category'], 'weekly')
    
    def test_calculate_duration_info_extended(self):
        """Test duration calculation for extended rental (10 days)"""
        start = self.base_datetime
        end = start + timedelta(days=10)
        
        result = RentalCalculator.calculate_duration_info(start, end)
        
        self.assertEqual(result['days'], 10.0)
        self.assertEqual(result['rate_category'], 'extended')
    
    def test_calculate_duration_info_mixed_days_hours(self):
        """Test duration calculation with mixed days and hours"""
        start = self.base_datetime
        end = start + timedelta(days=1, hours=3)
        
        result = RentalCalculator.calculate_duration_info(start, end)
        
        self.assertEqual(result['days_display'], '1 day 3 hours')
    
    def test_calculate_duration_invalid_range(self):
        """Test duration calculation with invalid date range"""
        start = self.base_datetime
        end = start - timedelta(hours=1)  # End before start
        
        with self.assertRaises(ValueError):
            RentalCalculator.calculate_duration_info(start, end)
    
    def test_calculate_base_rate_half_day(self):
        """Test base rate calculation for half day"""
        # Use exact decimal calculation to match service precision
        half_day_duration = float(Decimal('5') / Decimal('24'))
        rate = RentalCalculator.calculate_base_rate(self.trailer, half_day_duration)
        self.assertEqual(rate, self.trailer.half_day_rate)
    
    def test_calculate_base_rate_daily_1_day(self):
        """Test base rate calculation for 1 day"""
        rate = RentalCalculator.calculate_base_rate(self.trailer, 1.0)
        self.assertEqual(rate, self.trailer.daily_rate * 1)
    
    def test_calculate_base_rate_daily_partial_day_over_half(self):
        """Test base rate calculation for partial day over half-day threshold"""
        rate = RentalCalculator.calculate_base_rate(self.trailer, 1.3)  # 1 full day + 0.3 (over half-day) = 2 full days
        self.assertEqual(rate, self.trailer.daily_rate * 2)
    
    def test_calculate_base_rate_daily_max(self):
        """Test base rate calculation for max daily rate (4 days)"""
        rate = RentalCalculator.calculate_base_rate(self.trailer, 4.0)
        self.assertEqual(rate, self.trailer.daily_rate * 4)
    
    def test_calculate_base_rate_weekly(self):
        """Test base rate calculation for weekly rate (5-7 days)"""
        for days in [5, 6, 7]:
            rate = RentalCalculator.calculate_base_rate(self.trailer, days)
            self.assertEqual(rate, self.trailer.weekly_rate)
    
    def test_calculate_base_rate_extended(self):
        """Test base rate calculation for extended rate (8+ days)"""
        rate = RentalCalculator.calculate_base_rate(self.trailer, 10.0)
        expected_daily = self.trailer.weekly_rate / RentalCalculator.WEEKLY_RATE_DIVISOR
        expected_rate = expected_daily * 10
        self.assertEqual(rate, expected_rate)
    
    def test_calculate_base_rate_custom_rate(self):
        """Test base rate calculation with custom rate override"""
        custom_rate = Decimal('100.00')
        rate = RentalCalculator.calculate_base_rate(self.trailer, 2.0, custom_rate)
        self.assertEqual(rate, custom_rate)
    
    def test_calculate_base_rate_half_day_increments(self):
        """Test base rate calculation for half-day increments after full days"""
        # 1.5 days = 1 day + half day
        half_day_fraction = float(Decimal('5') / Decimal('24'))  # Exact half-day threshold
        rate_1_5 = RentalCalculator.calculate_base_rate(self.trailer, 1.0 + half_day_fraction)
        expected_1_5 = self.trailer.daily_rate * 1 + self.trailer.half_day_rate
        self.assertEqual(rate_1_5, expected_1_5)
        
        # 2.5 days = 2 days + half day
        rate_2_5 = RentalCalculator.calculate_base_rate(self.trailer, 2.0 + half_day_fraction)
        expected_2_5 = self.trailer.daily_rate * 2 + self.trailer.half_day_rate
        self.assertEqual(rate_2_5, expected_2_5)
        
        # 3.5 days = 3 days + half day
        rate_3_5 = RentalCalculator.calculate_base_rate(self.trailer, 3.0 + half_day_fraction)
        expected_3_5 = self.trailer.daily_rate * 3 + self.trailer.half_day_rate
        self.assertEqual(rate_3_5, expected_3_5)
        
        # 4.5 days = 4 days + half day (still in daily rate territory)
        rate_4_5 = RentalCalculator.calculate_base_rate(self.trailer, 4.0 + half_day_fraction)
        expected_4_5 = self.trailer.daily_rate * 4 + self.trailer.half_day_rate
        self.assertEqual(rate_4_5, expected_4_5)
    
    def test_calculate_base_rate_edge_cases_around_half_day_threshold(self):
        """Test edge cases around the half-day threshold"""
        # Slightly under half-day threshold should get half-day rate
        under_threshold = float(Decimal('4.9') / Decimal('24'))  # 4.9 hours
        rate_under = RentalCalculator.calculate_base_rate(self.trailer, 1.0 + under_threshold)
        expected_under = self.trailer.daily_rate * 1 + self.trailer.half_day_rate
        self.assertEqual(rate_under, expected_under)
        
        # Slightly over half-day threshold should get full day rate
        over_threshold = float(Decimal('5.1') / Decimal('24'))  # 5.1 hours
        rate_over = RentalCalculator.calculate_base_rate(self.trailer, 1.0 + over_threshold)
        expected_over = self.trailer.daily_rate * 2
        self.assertEqual(rate_over, expected_over)
    
    def test_calculate_base_rate_transition_to_weekly(self):
        """Test transition from daily with half-day to weekly pricing"""
        # 4.5 days should use daily + half-day pricing (special case for exactly 0.5)
        rate_4_5 = RentalCalculator.calculate_base_rate(self.trailer, 4.5)
        expected_4_5 = self.trailer.daily_rate * 4 + self.trailer.half_day_rate
        self.assertEqual(rate_4_5, expected_4_5)
        
        # 4.6 days should transition to weekly pricing (over 4.5 threshold)
        rate_4_6 = RentalCalculator.calculate_base_rate(self.trailer, 4.6)
        self.assertEqual(rate_4_6, self.trailer.weekly_rate)
        
        # 5.0 days should definitely use weekly pricing
        rate_5_0 = RentalCalculator.calculate_base_rate(self.trailer, 5.0)
        self.assertEqual(rate_5_0, self.trailer.weekly_rate)
    
    def test_calculate_addon_costs_all_addons(self):
        """Test addon cost calculation with all addons"""
        result = RentalCalculator.calculate_addon_costs(
            self.settings,
            includes_winch=True,
            includes_hitch_bar=True,
            furniture_blanket_count=3,
            strap_chain_count=2,
            has_evening_pickup=True
        )
        
        expected_total = (
            self.settings.winch_price +
            self.settings.hitch_bar_price +
            (self.settings.furniture_blanket_price * 3) +
            (self.settings.strap_chain_price * 2) +
            self.settings.evening_pickup_price
        )
        
        self.assertEqual(result['winch_cost'], self.settings.winch_price)
        self.assertEqual(result['hitch_bar_cost'], self.settings.hitch_bar_price)
        self.assertEqual(result['furniture_blanket_cost'], self.settings.furniture_blanket_price * 3)
        self.assertEqual(result['strap_chain_cost'], self.settings.strap_chain_price * 2)
        self.assertEqual(result['evening_pickup_cost'], self.settings.evening_pickup_price)
        self.assertEqual(result['total_addon_cost'], expected_total)
    
    def test_calculate_addon_costs_no_addons(self):
        """Test addon cost calculation with no addons"""
        result = RentalCalculator.calculate_addon_costs(self.settings)
        
        for key in result:
            self.assertEqual(result[key], Decimal('0'))
    
    def test_calculate_addon_costs_no_settings(self):
        """Test addon cost calculation with no settings"""
        result = RentalCalculator.calculate_addon_costs(None)
        
        for key in result:
            self.assertEqual(result[key], Decimal('0'))
    
    def test_calculate_totals(self):
        """Test total calculation with all components"""
        base_rate = Decimal('75.00')
        addon_costs = Decimal('25.00')
        extra_mileage = Decimal('10.00')
        tax_rate = Decimal('8.25')
        down_payment = Decimal('50.00')
        
        result = RentalCalculator.calculate_totals(
            base_rate, addon_costs, extra_mileage, tax_rate, down_payment
        )
        
        expected_subtotal = base_rate + addon_costs + extra_mileage  # 110.00
        expected_tax = expected_subtotal * (tax_rate / Decimal('100'))  # 9.075
        expected_total = expected_subtotal + expected_tax  # 119.075
        expected_balance = expected_total - down_payment  # 69.075
        
        self.assertEqual(result['subtotal'], expected_subtotal)
        self.assertEqual(result['tax_amount'], expected_tax)
        self.assertEqual(result['total_amount'], expected_total)
        self.assertEqual(result['balance_due'], expected_balance)
    
    def test_calculate_complete_quote_half_day(self):
        """Test complete quote calculation for half day rental"""
        start = self.base_datetime
        end = start + timedelta(hours=4)  # 4 hours = half day
        
        quote = RentalCalculator.calculate_complete_quote(
            trailer=self.trailer,
            start_datetime=start,
            end_datetime=end,
            settings=self.settings,
            includes_winch=True
        )
        
        # Verify all components are present
        self.assertIn('duration_info', quote)
        self.assertIn('base_rate', quote)
        self.assertIn('addon_costs', quote)
        self.assertIn('subtotal', quote)
        self.assertIn('tax_amount', quote)
        self.assertIn('total_amount', quote)
        self.assertIn('balance_due', quote)
        
        # Verify calculations
        self.assertTrue(quote['duration_info']['is_half_day'])
        self.assertEqual(quote['base_rate'], self.trailer.half_day_rate)
        self.assertEqual(quote['addon_costs']['winch_cost'], self.settings.winch_price)
    
    def test_calculate_complete_quote_weekly(self):
        """Test complete quote calculation for weekly rental"""
        start = self.base_datetime
        end = start + timedelta(days=6)  # 6 days = weekly rate
        
        quote = RentalCalculator.calculate_complete_quote(
            trailer=self.trailer,
            start_datetime=start,
            end_datetime=end,
            settings=self.settings
        )
        
        self.assertEqual(quote['duration_info']['rate_category'], 'weekly')
        self.assertEqual(quote['base_rate'], self.trailer.weekly_rate)
    
    def test_get_pricing_rules_display(self):
        """Test pricing rules display formatting"""
        rules = RentalCalculator.get_pricing_rules_display()
        
        self.assertIsInstance(rules, list)
        self.assertTrue(len(rules) >= 4)
        
        # Check that rules contain expected information
        self.assertTrue(any('5 hours or less' in rule for rule in rules))
        self.assertTrue(any('1-4 Days' in rule for rule in rules))
        self.assertTrue(any('5-7 Days' in rule for rule in rules))
        self.assertTrue(any('8+ Days' in rule for rule in rules))
    
    def test_get_calculation_constants(self):
        """Test calculation constants retrieval"""
        constants = RentalCalculator.get_calculation_constants()
        
        self.assertEqual(constants['HALF_DAY_HOURS'], 5)
        self.assertEqual(constants['HALF_DAY_THRESHOLD'], 5.0/24)
        self.assertEqual(constants['DAILY_RATE_MAX_DAYS'], 4)
        self.assertEqual(constants['WEEKLY_RATE_MAX_DAYS'], 7)
        self.assertEqual(constants['WEEKLY_RATE_DIVISOR'], 6)
    
    def test_precision_edge_cases(self):
        """Test edge cases for decimal precision"""
        # Test exactly 5 hours
        start = self.base_datetime
        end = start + timedelta(hours=5, seconds=0)
        
        duration_info = RentalCalculator.calculate_duration_info(start, end)
        self.assertTrue(duration_info['is_half_day'])
        
        # Test 5 hours + 1 second
        end = start + timedelta(hours=5, seconds=1)
        duration_info = RentalCalculator.calculate_duration_info(start, end)
        self.assertFalse(duration_info['is_half_day'])
    
    def test_rate_calculation_consistency(self):
        """Test that rate calculations are consistent across different methods"""
        start = self.base_datetime
        end = start + timedelta(days=3)
        
        # Calculate using complete quote
        quote = RentalCalculator.calculate_complete_quote(
            trailer=self.trailer,
            start_datetime=start,
            end_datetime=end,
            settings=self.settings
        )
        
        # Calculate using individual methods
        duration_info = RentalCalculator.calculate_duration_info(start, end)
        base_rate = RentalCalculator.calculate_base_rate(self.trailer, duration_info['days'])
        
        # Should be the same
        self.assertEqual(quote['base_rate'], base_rate)
        self.assertEqual(quote['duration_info']['days'], duration_info['days']) 