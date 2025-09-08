from django.test import TestCase
from django.core.exceptions import ValidationError
from rental_scheduler.models import Trailer, TrailerCategory, Customer


class TrailerModelTest(TestCase):
    """Test cases for the enhanced Trailer model"""
    
    def setUp(self):
        """Set up test data"""
        self.category = TrailerCategory.objects.create(category="Test Category")
        self.customer = Customer.objects.create(
            business_name="Test Company",
            phone="555-123-4567"
        )
    
    def test_trailer_creation_basic(self):
        """Test creating a basic trailer"""
        trailer = Trailer.objects.create(
            category=self.category,
            number="T001",
            model="Test Model",
            hauling_capacity=5000.00
        )
        
        self.assertEqual(trailer.display_name, "T001 - Test Model")
        self.assertEqual(trailer.is_rental_trailer, True)
        self.assertEqual(trailer.is_available, True)
        self.assertEqual(str(trailer), "T001 - Test Model")
    
    def test_trailer_creation_with_customer(self):
        """Test creating a customer-owned trailer"""
        trailer = Trailer.objects.create(
            category=self.category,
            number="T002",
            model="Customer Model",
            hauling_capacity=3000.00,
            customer=self.customer,
            is_rental_trailer=False
        )
        
        self.assertEqual(trailer.display_name, "T002 - Customer Model")
        self.assertEqual(trailer.is_rental_trailer, False)
        self.assertEqual(str(trailer), "T002 - Customer Model (Owned by Test Company)")
    
    def test_trailer_creation_with_identification(self):
        """Test creating a trailer with identification fields"""
        trailer = Trailer.objects.create(
            category=self.category,
            number="T003",
            model="Identified Model",
            hauling_capacity=4000.00,
            serial_number="SN123456",
            color="Red",
            description="Large utility trailer"
        )
        
        self.assertEqual(trailer.serial_number, "SN123456")
        self.assertEqual(trailer.color, "Red")
        self.assertEqual(trailer.description, "Large utility trailer")
        self.assertIn("SN123456", trailer.search_text)
        self.assertIn("Red", trailer.search_text)
        self.assertIn("Large utility trailer", trailer.search_text)
    
    def test_trailer_creation_with_dimensions(self):
        """Test creating a trailer with dimensions"""
        trailer = Trailer.objects.create(
            category=self.category,
            number="T004",
            model="Dimensional Model",
            hauling_capacity=6000.00,
            length=20.0,
            width=8.5,
            height=7.0
        )
        
        self.assertEqual(trailer.dimensions, "20.0'L x 8.5'W x 7.0'H")
        self.assertEqual(trailer.length, 20.0)
        self.assertEqual(trailer.width, 8.5)
        self.assertEqual(trailer.height, 7.0)
    
    def test_trailer_creation_with_rates(self):
        """Test creating a trailer with rental rates"""
        trailer = Trailer.objects.create(
            category=self.category,
            number="T005",
            model="Rental Model",
            hauling_capacity=5000.00,
            half_day_rate=50.00,
            daily_rate=100.00,
            weekly_rate=500.00
        )
        
        self.assertEqual(trailer.half_day_rate, 50.00)
        self.assertEqual(trailer.daily_rate, 100.00)
        self.assertEqual(trailer.weekly_rate, 500.00)
    
    def test_trailer_validation_duplicate_number(self):
        """Test that validation fails for duplicate trailer numbers"""
        Trailer.objects.create(
            category=self.category,
            number="T006",
            model="First Model",
            hauling_capacity=5000.00
        )
        
        trailer2 = Trailer(
            category=self.category,
            number="T006",  # Duplicate number
            model="Second Model",
            hauling_capacity=6000.00
        )
        
        with self.assertRaises(ValidationError):
            trailer2.full_clean()
    
    def test_trailer_validation_duplicate_serial(self):
        """Test that validation fails for duplicate serial numbers"""
        Trailer.objects.create(
            category=self.category,
            number="T007",
            model="First Model",
            hauling_capacity=5000.00,
            serial_number="SN789"
        )
        
        trailer2 = Trailer(
            category=self.category,
            number="T008",
            model="Second Model",
            hauling_capacity=6000.00,
            serial_number="SN789"  # Duplicate serial
        )
        
        with self.assertRaises(ValidationError):
            trailer2.full_clean()
    
    def test_trailer_validation_negative_dimensions(self):
        """Test that validation fails for negative dimensions"""
        trailer = Trailer(
            category=self.category,
            number="T009",
            model="Invalid Model",
            hauling_capacity=5000.00,
            length=-10.0  # Negative length
        )
        
        with self.assertRaises(ValidationError):
            trailer.full_clean()
    
    def test_trailer_validation_zero_capacity(self):
        """Test that validation fails for zero hauling capacity"""
        trailer = Trailer(
            category=self.category,
            number="T010",
            model="Invalid Model",
            hauling_capacity=0.00  # Zero capacity
        )
        
        with self.assertRaises(ValidationError):
            trailer.full_clean()
    
    def test_trailer_search_text(self):
        """Test the search_text property"""
        trailer = Trailer.objects.create(
            category=self.category,
            number="T011",
            model="Searchable Model",
            hauling_capacity=5000.00,
            serial_number="SN999",
            color="Blue",
            description="Excellent condition",
            customer=self.customer
        )
        
        search_text = trailer.search_text
        self.assertIn("T011", search_text)
        self.assertIn("Searchable Model", search_text)
        self.assertIn("SN999", search_text)
        self.assertIn("Blue", search_text)
        self.assertIn("Excellent condition", search_text)
        self.assertIn("Test Company", search_text)
    
    def test_trailer_dimensions_partial(self):
        """Test dimensions property with partial data"""
        trailer = Trailer.objects.create(
            category=self.category,
            number="T012",
            model="Partial Model",
            hauling_capacity=5000.00,
            length=15.0,
            width=7.0
            # No height
        )
        
        self.assertEqual(trailer.dimensions, "15.0'L x 7.0'W")
    
    def test_trailer_dimensions_empty(self):
        """Test dimensions property with no dimension data"""
        trailer = Trailer.objects.create(
            category=self.category,
            number="T013",
            model="No Dimensions Model",
            hauling_capacity=5000.00
        )
        
        self.assertIsNone(trailer.dimensions)
    
    def test_trailer_is_rentable_property(self):
        """Test the is_rentable property"""
        # Test rentable trailer
        trailer1 = Trailer.objects.create(
            category=self.category,
            number="T014",
            model="Rentable Model",
            hauling_capacity=5000.00,
            is_rental_trailer=True,
            is_available=True
        )
        self.assertTrue(trailer1.is_rentable)
        
        # Test non-rental trailer
        trailer2 = Trailer.objects.create(
            category=self.category,
            number="T015",
            model="Non-Rental Model",
            hauling_capacity=5000.00,
            is_rental_trailer=False,
            is_available=True
        )
        self.assertFalse(trailer2.is_rentable)
        
        # Test unavailable trailer
        trailer3 = Trailer.objects.create(
            category=self.category,
            number="T016",
            model="Unavailable Model",
            hauling_capacity=5000.00,
            is_rental_trailer=True,
            is_available=False
        )
        self.assertFalse(trailer3.is_rentable)

