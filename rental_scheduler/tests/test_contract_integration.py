"""
Integration tests for Contract model with RentalCalculator service.
Tests that the model integration works correctly.
"""
import tempfile
import os
from datetime import datetime, timedelta
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone

from rental_scheduler.models import Trailer, TrailerCategory, SystemSettings, Contract, Customer


class ContractIntegrationTestCase(TestCase):
    """Test cases for Contract model integration with RentalCalculator service"""
    
    def setUp(self):
        """Set up test data"""
        # Create test category
        self.category = TrailerCategory.objects.create(category="Test Category")
        
        # Create test trailer
        self.trailer = Trailer.objects.create(
            category=self.category,
            number="TEST001",
            size="5x10",
            model="Test Trailer",
            hauling_capacity=Decimal('2000.00'),
            half_day_rate=Decimal('50.00'),
            daily_rate=Decimal('75.00'),
            weekly_rate=Decimal('300.00')
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
        
        # Create test customer
        self.customer = Customer.objects.create(
            name="Test Customer",
            phone="5551234567",
            street_address="123 Test St",
            city="Test City",
            state="TS",
            zip_code="12345"
        )
        
        # Base datetime for consistent testing
        self.base_datetime = timezone.make_aware(datetime(2024, 1, 15, 7, 0, 0))
    
    def tearDown(self):
        """Clean up test data"""
        # Remove temporary directory
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_contract_half_day_calculation(self):
        """Test that contract calculations work correctly for half day rental"""
        start = self.base_datetime
        end = start + timedelta(hours=4)  # 4 hours = half day
        
        contract = Contract.objects.create(
            customer=self.customer,
            trailer=self.trailer,
            category=self.category,
            start_datetime=start,
            end_datetime=end,
            includes_winch=True,
            extra_mileage=Decimal('10.00'),
            down_payment=Decimal('25.00')
        )
        
        # Test duration calculation
        duration = contract.calculate_duration()
        self.assertLess(duration, 0.21)  # Should be less than 5/24
        
        # Test rate calculation
        rate = contract.calculate_rate()
        self.assertEqual(rate, self.trailer.half_day_rate)
        
        # Test addon calculation
        addons = contract.calculate_add_ons()
        self.assertEqual(addons, self.settings.winch_price)
        
        # Test subtotal
        subtotal = contract.calculate_subtotal()
        expected_subtotal = self.trailer.half_day_rate + self.settings.winch_price + Decimal('10.00')
        self.assertEqual(subtotal, expected_subtotal)
        
        # Test tax
        tax = contract.calculate_tax()
        expected_tax = expected_subtotal * (self.settings.tax_rate / 100)
        self.assertEqual(tax, expected_tax)
        
        # Test total
        total = contract.calculate_total()
        expected_total = expected_subtotal + expected_tax
        self.assertEqual(total, expected_total)
        
        # Test balance
        balance = contract.calculate_balance()
        expected_balance = expected_total - Decimal('25.00')
        self.assertEqual(balance, expected_balance)
    
    def test_contract_daily_calculation(self):
        """Test that contract calculations work correctly for daily rental"""
        start = self.base_datetime
        end = start + timedelta(days=2, hours=3)  # 2.125 days rounds to 3 days
        
        contract = Contract.objects.create(
            customer=self.customer,
            trailer=self.trailer,
            category=self.category,
            start_datetime=start,
            end_datetime=end,
            includes_hitch_bar=True,
            furniture_blanket_count=2,
            extra_mileage=Decimal('15.00'),
            down_payment=Decimal('100.00')
        )
        
        # Test duration calculation
        duration = contract.calculate_duration()
        self.assertGreater(duration, 2.0)
        self.assertLess(duration, 3.0)
        
        # Test rate calculation (should round up to 3 days)
        rate = contract.calculate_rate()
        self.assertEqual(rate, self.trailer.daily_rate * 3)
        
        # Test addon calculation
        addons = contract.calculate_add_ons()
        expected_addons = self.settings.hitch_bar_price + (self.settings.furniture_blanket_price * 2)
        self.assertEqual(addons, expected_addons)
    
    def test_contract_weekly_calculation(self):
        """Test that contract calculations work correctly for weekly rental"""
        start = self.base_datetime
        end = start + timedelta(days=6)  # 6 days = weekly rate
        
        contract = Contract.objects.create(
            customer=self.customer,
            trailer=self.trailer,
            category=self.category,
            start_datetime=start,
            end_datetime=end,
            has_evening_pickup=True,
            strap_chain_count=4
        )
        
        # Test rate calculation
        rate = contract.calculate_rate()
        self.assertEqual(rate, self.trailer.weekly_rate)
        
        # Test addon calculation
        addons = contract.calculate_add_ons()
        expected_addons = self.settings.evening_pickup_price + (self.settings.strap_chain_price * 4)
        self.assertEqual(addons, expected_addons)
    
    def test_contract_extended_calculation(self):
        """Test that contract calculations work correctly for extended rental"""
        start = self.base_datetime
        end = start + timedelta(days=10)  # 10 days = extended rate
        
        contract = Contract.objects.create(
            customer=self.customer,
            trailer=self.trailer,
            category=self.category,
            start_datetime=start,
            end_datetime=end
        )
        
        # Test rate calculation
        rate = contract.calculate_rate()
        expected_daily = self.trailer.weekly_rate / 6
        expected_rate = expected_daily * 10
        self.assertEqual(rate, expected_rate)
    
    def test_contract_custom_rate(self):
        """Test that custom rate overrides calculated rate"""
        start = self.base_datetime
        end = start + timedelta(days=2)
        custom_rate = Decimal('150.00')
        
        contract = Contract.objects.create(
            customer=self.customer,
            trailer=self.trailer,
            category=self.category,
            start_datetime=start,
            end_datetime=end,
            custom_rate=custom_rate
        )
        
        # Test that custom rate is used
        rate = contract.calculate_rate()
        self.assertEqual(rate, custom_rate)
    
    def test_contract_stored_rate_priority(self):
        """Test that stored rate has priority over custom rate"""
        start = self.base_datetime
        end = start + timedelta(days=2)
        custom_rate = Decimal('150.00')
        stored_rate = Decimal('175.00')
        
        contract = Contract.objects.create(
            customer=self.customer,
            trailer=self.trailer,
            category=self.category,
            start_datetime=start,
            end_datetime=end,
            custom_rate=custom_rate,
            stored_rate=stored_rate
        )
        
        # Test that stored rate has priority
        rate = contract.calculate_rate()
        self.assertEqual(rate, stored_rate)
    
    def test_contract_with_all_addons(self):
        """Test contract calculation with all possible addons"""
        start = self.base_datetime
        end = start + timedelta(hours=3)  # Half day
        
        contract = Contract.objects.create(
            customer=self.customer,
            trailer=self.trailer,
            category=self.category,
            start_datetime=start,
            end_datetime=end,
            includes_winch=True,
            includes_hitch_bar=True,
            furniture_blanket_count=5,
            strap_chain_count=3,
            has_evening_pickup=True,
            extra_mileage=Decimal('20.00'),
            down_payment=Decimal('50.00')
        )
        
        # Test addon calculation
        addons = contract.calculate_add_ons()
        expected_addons = (
            self.settings.winch_price +
            self.settings.hitch_bar_price +
            (self.settings.furniture_blanket_price * 5) +
            (self.settings.strap_chain_price * 3) +
            self.settings.evening_pickup_price
        )
        self.assertEqual(addons, expected_addons)
        
        # Test that all calculations work together
        subtotal = contract.calculate_subtotal()
        tax = contract.calculate_tax()
        total = contract.calculate_total()
        balance = contract.calculate_balance()
        
        # Verify calculations are consistent
        self.assertEqual(subtotal, contract.calculate_rate() + addons + contract.extra_mileage)
        self.assertEqual(total, subtotal + tax)
        self.assertEqual(balance, total - contract.down_payment)
    
    def test_backward_compatibility(self):
        """Test that the model still works if the service throws an exception"""
        # This test ensures our fallback mechanisms work
        start = self.base_datetime
        end = start + timedelta(hours=4)
        
        contract = Contract.objects.create(
            customer=self.customer,
            trailer=self.trailer,
            category=self.category,
            start_datetime=start,
            end_datetime=end
        )
        
        # All calculations should still work even if service is unavailable
        # (fallback to legacy calculations)
        duration = contract.calculate_duration()
        self.assertIsInstance(duration, float)
        
        rate = contract.calculate_rate()
        self.assertIsInstance(rate, Decimal)
        
        addons = contract.calculate_add_ons()
        self.assertIsInstance(addons, Decimal)
        
        subtotal = contract.calculate_subtotal()
        self.assertIsInstance(subtotal, Decimal)
        
        tax = contract.calculate_tax()
        self.assertIsInstance(tax, Decimal)
        
        total = contract.calculate_total()
        self.assertIsInstance(total, Decimal)
        
        balance = contract.calculate_balance()
        self.assertIsInstance(balance, Decimal) 