from django.test import TestCase
from django.core.exceptions import ValidationError
from rental_scheduler.models import Customer


class CustomerModelTest(TestCase):
    """Test cases for the enhanced Customer model"""
    
    def test_customer_creation_with_business_name(self):
        """Test creating a customer with business name"""
        customer = Customer.objects.create(
            business_name="ABC Company",
            contact_name="John Doe",
            phone="555-123-4567",
            email="john@abc.com",
            address_line1="123 Main St",
            city="Anytown",
            state="CA",
            postal_code="12345"
        )
        
        self.assertEqual(customer.display_name, "ABC Company")
        self.assertEqual(customer.primary_phone, "555-123-4567")
        self.assertEqual(customer.full_address, "123 Main St, Anytown, CA, 12345")
        self.assertEqual(str(customer), "ABC Company - John Doe")
    
    def test_customer_creation_with_contact_name_only(self):
        """Test creating a customer with contact name only"""
        customer = Customer.objects.create(
            contact_name="Jane Smith",
            phone="555-987-6543",
            alt_phone="555-111-2222"
        )
        
        self.assertEqual(customer.display_name, "Jane Smith")
        self.assertEqual(customer.primary_phone, "555-987-6543")
        self.assertEqual(str(customer), "Jane Smith")
    
    def test_customer_creation_with_legacy_fields(self):
        """Test creating a customer with legacy fields"""
        customer = Customer.objects.create(
            name="Legacy Customer",
            phone="555-555-5555",
            street_address="456 Old St",
            zip_code="54321"
        )
        
        self.assertEqual(customer.display_name, "Legacy Customer")
        self.assertEqual(customer.primary_phone, "555-555-5555")
        self.assertEqual(str(customer), "Legacy Customer")
    
    def test_customer_validation_no_name(self):
        """Test that validation fails when no name fields are provided"""
        customer = Customer(
            phone="555-123-4567"
        )
        
        with self.assertRaises(ValidationError):
            customer.full_clean()
    
    def test_customer_validation_no_phone(self):
        """Test that validation fails when no phone numbers are provided"""
        customer = Customer(
            business_name="Test Company"
        )
        
        with self.assertRaises(ValidationError):
            customer.full_clean()
    
    def test_customer_validation_success(self):
        """Test that validation passes with valid data"""
        customer = Customer(
            business_name="Valid Company",
            phone="555-123-4567"
        )
        
        # Should not raise ValidationError
        customer.full_clean()
    
    def test_customer_primary_phone_fallback(self):
        """Test that primary_phone falls back to alt_phone when phone is empty"""
        customer = Customer.objects.create(
            business_name="Test Company",
            alt_phone="555-999-8888"
        )
        
        self.assertEqual(customer.primary_phone, "555-999-8888")
    
    def test_customer_full_address_formatting(self):
        """Test full_address property formatting"""
        customer = Customer.objects.create(
            business_name="Address Test",
            phone="555-123-4567",
            address_line1="123 Main St",
            address_line2="Suite 100",
            city="Anytown",
            state="CA",
            postal_code="12345"
        )
        
        expected = "123 Main St, Suite 100, Anytown, CA, 12345"
        self.assertEqual(customer.full_address, expected)
    
    def test_customer_full_address_partial(self):
        """Test full_address with partial address data"""
        customer = Customer.objects.create(
            business_name="Partial Address",
            phone="555-123-4567",
            city="Anytown",
            state="CA"
        )
        
        expected = "Anytown, CA"
        self.assertEqual(customer.full_address, expected)
    
    def test_customer_full_address_empty(self):
        """Test full_address when no address data is provided"""
        customer = Customer.objects.create(
            business_name="No Address",
            phone="555-123-4567"
        )
        
        self.assertIsNone(customer.full_address)
    
    def test_customer_str_method_priority(self):
        """Test that __str__ method uses the correct priority order"""
        # Test business_name + contact_name
        customer1 = Customer.objects.create(
            business_name="Company A",
            contact_name="Person A",
            phone="555-111-1111"
        )
        self.assertEqual(str(customer1), "Company A - Person A")
        
        # Test business_name only
        customer2 = Customer.objects.create(
            business_name="Company B",
            phone="555-222-2222"
        )
        self.assertEqual(str(customer2), "Company B")
        
        # Test contact_name only
        customer3 = Customer.objects.create(
            contact_name="Person C",
            phone="555-333-3333"
        )
        self.assertEqual(str(customer3), "Person C")
        
        # Test legacy name fallback
        customer4 = Customer.objects.create(
            name="Legacy Name",
            phone="555-444-4444"
        )
        self.assertEqual(str(customer4), "Legacy Name")
        
        # Test ID fallback
        customer5 = Customer.objects.create(
            phone="555-555-5555"
        )
        self.assertEqual(str(customer5), f"Customer #{customer5.id}")

