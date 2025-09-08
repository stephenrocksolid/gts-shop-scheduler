from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from rental_scheduler.models import (
    WorkOrder, WorkOrderLine, Job, Calendar, Customer, Trailer, TrailerCategory
)


class WorkOrderModelTest(TestCase):
    """Test cases for the WorkOrder model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.calendar = Calendar.objects.create(
            name="Test Calendar",
            color="#3B82F6"
        )
        
        self.customer = Customer.objects.create(
            business_name="Test Company",
            contact_name="John Doe",
            phone="555-123-4567"
        )
        
        self.category = TrailerCategory.objects.create(
            category="Test Category"
        )
        
        self.trailer = Trailer.objects.create(
            category=self.category,
            number="T001",
            model="Test Model",
            hauling_capacity=5000.00
        )
        
        self.job = Job.objects.create(
            calendar=self.calendar,
            customer=self.customer,
            trailer=self.trailer,
            start_dt=timezone.now() + timedelta(days=1),
            end_dt=timezone.now() + timedelta(days=1, hours=2)
        )
    
    def test_workorder_creation_basic(self):
        """Test creating a basic work order"""
        work_order = WorkOrder.objects.create(
            job=self.job,
            wo_number="WO-2024-001",
            wo_date=timezone.now().date()
        )
        
        self.assertEqual(work_order.wo_number, "WO-2024-001")
        self.assertEqual(work_order.job, self.job)
        self.assertEqual(work_order.wo_date, timezone.now().date())
        self.assertEqual(str(work_order), "WO-2024-001 - Test Company")
        self.assertEqual(work_order.total_amount, Decimal('0.00'))
        self.assertEqual(work_order.line_count, 0)
    
    def test_workorder_creation_with_notes(self):
        """Test creating a work order with notes"""
        work_order = WorkOrder.objects.create(
            job=self.job,
            wo_number="WO-2024-002",
            wo_date=timezone.now().date(),
            notes="Test work order notes"
        )
        
        self.assertEqual(work_order.notes, "Test work order notes")
    
    def test_workorder_total_amount_calculation(self):
        """Test work order total amount calculation"""
        work_order = WorkOrder.objects.create(
            job=self.job,
            wo_number="WO-2024-003",
            wo_date=timezone.now().date()
        )
        
        # Create line items
        line1 = WorkOrderLine.objects.create(
            work_order=work_order,
            description="Labor",
            qty=Decimal('2.0'),
            rate=Decimal('50.00')
        )
        
        line2 = WorkOrderLine.objects.create(
            work_order=work_order,
            description="Parts",
            qty=Decimal('1.0'),
            rate=Decimal('25.00')
        )
        
        expected_total = Decimal('125.00')  # (2 * 50) + (1 * 25)
        self.assertEqual(work_order.total_amount, expected_total)
        self.assertEqual(work_order.line_count, 2)
    
    def test_workorder_validation_empty_number(self):
        """Test that validation fails for empty work order number"""
        work_order = WorkOrder(
            job=self.job,
            wo_number="",  # Empty number
            wo_date=timezone.now().date()
        )
        
        with self.assertRaises(ValidationError):
            work_order.full_clean()
    
    def test_workorder_validation_whitespace_number(self):
        """Test that validation fails for whitespace-only work order number"""
        work_order = WorkOrder(
            job=self.job,
            wo_number="   ",  # Whitespace only
            wo_date=timezone.now().date()
        )
        
        with self.assertRaises(ValidationError):
            work_order.full_clean()
    
    def test_workorder_meta_ordering(self):
        """Test work order meta ordering"""
        # Create work orders with different dates
        work_order1 = WorkOrder.objects.create(
            job=self.job,
            wo_number="WO-2024-001",
            wo_date=timezone.now().date()
        )
        
        work_order2 = WorkOrder.objects.create(
            job=self.job,
            wo_number="WO-2024-002",
            wo_date=timezone.now().date() + timedelta(days=1)
        )
        
        work_orders = WorkOrder.objects.all()
        self.assertEqual(work_orders[0], work_order2)  # Newest date first
        self.assertEqual(work_orders[1], work_order1)


class WorkOrderLineModelTest(TestCase):
    """Test cases for the WorkOrderLine model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.calendar = Calendar.objects.create(
            name="Test Calendar",
            color="#3B82F6"
        )
        
        self.customer = Customer.objects.create(
            business_name="Test Company",
            contact_name="John Doe",
            phone="555-123-4567"
        )
        
        self.category = TrailerCategory.objects.create(
            category="Test Category"
        )
        
        self.trailer = Trailer.objects.create(
            category=self.category,
            number="T001",
            model="Test Model",
            hauling_capacity=5000.00
        )
        
        self.job = Job.objects.create(
            calendar=self.calendar,
            customer=self.customer,
            trailer=self.trailer,
            start_dt=timezone.now() + timedelta(days=1),
            end_dt=timezone.now() + timedelta(days=1, hours=2)
        )
        
        self.work_order = WorkOrder.objects.create(
            job=self.job,
            wo_number="WO-2024-001",
            wo_date=timezone.now().date()
        )
    
    def test_workorderline_creation_basic(self):
        """Test creating a basic work order line"""
        line = WorkOrderLine.objects.create(
            work_order=self.work_order,
            description="Test line item",
            qty=Decimal('1.0'),
            rate=Decimal('50.00')
        )
        
        self.assertEqual(line.description, "Test line item")
        self.assertEqual(line.qty, Decimal('1.0'))
        self.assertEqual(line.rate, Decimal('50.00'))
        self.assertEqual(line.total, Decimal('50.00'))
        self.assertEqual(str(line), "Test line item - Qty: 1.0 @ $50.00")
    
    def test_workorderline_creation_with_item_code(self):
        """Test creating a work order line with item code"""
        line = WorkOrderLine.objects.create(
            work_order=self.work_order,
            item_code="PART-001",
            description="Test part",
            qty=Decimal('2.0'),
            rate=Decimal('25.00')
        )
        
        self.assertEqual(line.item_code, "PART-001")
        self.assertEqual(line.total, Decimal('50.00'))
    
    def test_workorderline_total_calculation(self):
        """Test work order line total calculation"""
        line = WorkOrderLine.objects.create(
            work_order=self.work_order,
            description="Labor",
            qty=Decimal('3.5'),
            rate=Decimal('75.00')
        )
        
        expected_total = Decimal('262.50')  # 3.5 * 75.00
        self.assertEqual(line.total, expected_total)
    
    def test_workorderline_validation_negative_qty(self):
        """Test that validation fails for negative quantity"""
        line = WorkOrderLine(
            work_order=self.work_order,
            description="Test line",
            qty=Decimal('-1.0'),
            rate=Decimal('50.00')
        )
        
        with self.assertRaises(ValidationError):
            line.full_clean()
    
    def test_workorderline_validation_zero_qty(self):
        """Test that validation fails for zero quantity"""
        line = WorkOrderLine(
            work_order=self.work_order,
            description="Test line",
            qty=Decimal('0.0'),
            rate=Decimal('50.00')
        )
        
        with self.assertRaises(ValidationError):
            line.full_clean()
    
    def test_workorderline_validation_negative_rate(self):
        """Test that validation fails for negative rate"""
        line = WorkOrderLine(
            work_order=self.work_order,
            description="Test line",
            qty=Decimal('1.0'),
            rate=Decimal('-50.00')
        )
        
        with self.assertRaises(ValidationError):
            line.full_clean()
    
    def test_workorderline_validation_empty_description(self):
        """Test that validation fails for empty description"""
        line = WorkOrderLine(
            work_order=self.work_order,
            description="",  # Empty description
            qty=Decimal('1.0'),
            rate=Decimal('50.00')
        )
        
        with self.assertRaises(ValidationError):
            line.full_clean()
    
    def test_workorderline_validation_whitespace_description(self):
        """Test that validation fails for whitespace-only description"""
        line = WorkOrderLine(
            work_order=self.work_order,
            description="   ",  # Whitespace only
            qty=Decimal('1.0'),
            rate=Decimal('50.00')
        )
        
        with self.assertRaises(ValidationError):
            line.full_clean()
    
    def test_workorderline_save_with_total_calculation(self):
        """Test that total is calculated on save"""
        line = WorkOrderLine(
            work_order=self.work_order,
            description="Test line",
            qty=Decimal('2.5'),
            rate=Decimal('40.00')
        )
        
        # Total should be calculated on save
        line.save()
        expected_total = Decimal('100.00')  # 2.5 * 40.00
        self.assertEqual(line.total, expected_total)
    
    def test_workorderline_meta_ordering(self):
        """Test work order line meta ordering"""
        # Create lines with different creation times
        line1 = WorkOrderLine.objects.create(
            work_order=self.work_order,
            description="First line",
            qty=Decimal('1.0'),
            rate=Decimal('50.00')
        )
        
        line2 = WorkOrderLine.objects.create(
            work_order=self.work_order,
            description="Second line",
            qty=Decimal('1.0'),
            rate=Decimal('50.00')
        )
        
        lines = WorkOrderLine.objects.all()
        self.assertEqual(lines[0], line1)  # Oldest first
        self.assertEqual(lines[1], line2)


class WorkOrderIntegrationTest(TestCase):
    """Integration tests for WorkOrder and WorkOrderLine models"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.calendar = Calendar.objects.create(
            name="Test Calendar",
            color="#3B82F6"
        )
        
        self.customer = Customer.objects.create(
            business_name="Test Company",
            contact_name="John Doe",
            phone="555-123-4567"
        )
        
        self.category = TrailerCategory.objects.create(
            category="Test Category"
        )
        
        self.trailer = Trailer.objects.create(
            category=self.category,
            number="T001",
            model="Test Model",
            hauling_capacity=5000.00
        )
        
        self.job = Job.objects.create(
            calendar=self.calendar,
            customer=self.customer,
            trailer=self.trailer,
            start_dt=timezone.now() + timedelta(days=1),
            end_dt=timezone.now() + timedelta(days=1, hours=2)
        )
    
    def test_workorder_with_multiple_lines(self):
        """Test work order with multiple line items"""
        work_order = WorkOrder.objects.create(
            job=self.job,
            wo_number="WO-2024-001",
            wo_date=timezone.now().date(),
            notes="Complex repair work"
        )
        
        # Create multiple line items
        lines_data = [
            {"description": "Labor", "qty": Decimal('4.0'), "rate": Decimal('75.00')},
            {"description": "Parts - Brake Pads", "qty": Decimal('1.0'), "rate": Decimal('45.00')},
            {"description": "Parts - Rotors", "qty": Decimal('2.0'), "rate": Decimal('85.00')},
            {"description": "Shop Supplies", "qty": Decimal('1.0'), "rate": Decimal('15.00')},
        ]
        
        for line_data in lines_data:
            WorkOrderLine.objects.create(
                work_order=work_order,
                **line_data
            )
        
        # Verify totals
        expected_total = Decimal('470.00')  # (4*75) + (1*45) + (2*85) + (1*15)
        self.assertEqual(work_order.total_amount, expected_total)
        self.assertEqual(work_order.line_count, 4)
        
        # Verify line items are accessible
        lines = work_order.lines.all()
        self.assertEqual(len(lines), 4)
        
        # Verify line items are ordered by creation time
        self.assertEqual(lines[0].description, "Labor")
        self.assertEqual(lines[1].description, "Parts - Brake Pads")
        self.assertEqual(lines[2].description, "Parts - Rotors")
        self.assertEqual(lines[3].description, "Shop Supplies")
    
    def test_workorder_cascade_delete(self):
        """Test that deleting a work order deletes its lines"""
        work_order = WorkOrder.objects.create(
            job=self.job,
            wo_number="WO-2024-001",
            wo_date=timezone.now().date()
        )
        
        # Create line items
        WorkOrderLine.objects.create(
            work_order=work_order,
            description="Test line 1",
            qty=Decimal('1.0'),
            rate=Decimal('50.00')
        )
        
        WorkOrderLine.objects.create(
            work_order=work_order,
            description="Test line 2",
            qty=Decimal('1.0'),
            rate=Decimal('50.00')
        )
        
        # Verify lines exist
        self.assertEqual(WorkOrderLine.objects.count(), 2)
        
        # Delete work order
        work_order.delete()
        
        # Verify lines are also deleted
        self.assertEqual(WorkOrderLine.objects.count(), 0)
    
    def test_workorder_unique_constraints(self):
        """Test work order unique constraints"""
        # Create first work order
        WorkOrder.objects.create(
            job=self.job,
            wo_number="WO-2024-001",
            wo_date=timezone.now().date()
        )
        
        # Try to create another work order with the same number
        with self.assertRaises(Exception):  # Should raise IntegrityError
            WorkOrder.objects.create(
                job=self.job,
                wo_number="WO-2024-001",  # Duplicate number
                wo_date=timezone.now().date()
            )
    
    def test_workorderline_constraints(self):
        """Test work order line constraints"""
        work_order = WorkOrder.objects.create(
            job=self.job,
            wo_number="WO-2024-001",
            wo_date=timezone.now().date()
        )
        
        # Test negative quantity constraint
        with self.assertRaises(Exception):  # Should raise IntegrityError
            WorkOrderLine.objects.create(
                work_order=work_order,
                description="Test line",
                qty=Decimal('-1.0'),
                rate=Decimal('50.00')
            )
        
        # Test negative rate constraint
        with self.assertRaises(Exception):  # Should raise IntegrityError
            WorkOrderLine.objects.create(
                work_order=work_order,
                description="Test line",
                qty=Decimal('1.0'),
                rate=Decimal('-50.00')
            )
    
    def test_workorder_string_representation(self):
        """Test work order string representation"""
        work_order = WorkOrder.objects.create(
            job=self.job,
            wo_number="WO-2024-001",
            wo_date=timezone.now().date()
        )
        
        expected = "WO-2024-001 - Test Company"
        self.assertEqual(str(work_order), expected)
    
    def test_workorderline_string_representation(self):
        """Test work order line string representation"""
        work_order = WorkOrder.objects.create(
            job=self.job,
            wo_number="WO-2024-001",
            wo_date=timezone.now().date()
        )
        
        line = WorkOrderLine.objects.create(
            work_order=work_order,
            description="Labor",
            qty=Decimal('2.5'),
            rate=Decimal('75.00')
        )
        
        expected = "Labor - Qty: 2.5 @ $75.00"
        self.assertEqual(str(line), expected)

