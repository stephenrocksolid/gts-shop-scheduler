from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from rental_scheduler.models import Job, Calendar, Customer, Trailer, TrailerCategory


class JobModelTest(TestCase):
    """Test cases for the Job model"""
    
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
        
        self.start_dt = timezone.now() + timedelta(days=1)
        self.end_dt = self.start_dt + timedelta(hours=2)
    
    def test_job_creation_basic(self):
        """Test creating a basic job"""
        job = Job.objects.create(
            calendar=self.calendar,
            customer=self.customer,
            trailer=self.trailer,
            start_dt=self.start_dt,
            end_dt=self.end_dt
        )
        
        self.assertEqual(job.display_name, "Test Company")
        self.assertEqual(job.status, 'scheduled')
        self.assertEqual(job.repeat_type, 'none')
        self.assertFalse(job.all_day)
        self.assertFalse(job.is_deleted)
        self.assertEqual(str(job), "Test Company - T001 - Test Model (Scheduled)")
    
    def test_job_creation_with_overrides(self):
        """Test creating a job with contact and address overrides"""
        job = Job.objects.create(
            calendar=self.calendar,
            customer=self.customer,
            trailer=self.trailer,
            start_dt=self.start_dt,
            end_dt=self.end_dt,
            business_name="Override Company",
            contact_name="Jane Smith",
            phone="555-987-6543",
            address_line1="123 Override St",
            city="Override City",
            state="CA",
            postal_code="90210"
        )
        
        self.assertEqual(job.display_name, "Override Company")
        self.assertEqual(job.contact_info['name'], "Jane Smith")
        self.assertEqual(job.contact_info['phone'], "555-987-6543")
        self.assertEqual(job.address_info['line1'], "123 Override St")
        self.assertEqual(job.address_info['city'], "Override City")
    
    def test_job_creation_all_day(self):
        """Test creating an all-day job"""
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=1)
        
        job = Job.objects.create(
            calendar=self.calendar,
            customer=self.customer,
            trailer=self.trailer,
            start_dt=timezone.make_aware(datetime.combine(start_date, datetime.min.time())),
            end_dt=timezone.make_aware(datetime.combine(end_date, datetime.min.time())),
            all_day=True
        )
        
        self.assertTrue(job.all_day)
        self.assertEqual(job.duration_hours, 24.0)
    
    def test_job_creation_with_repeat_type(self):
        """Test creating a job with repeat_type settings"""
        job = Job.objects.create(
            calendar=self.calendar,
            customer=self.customer,
            trailer=self.trailer,
            start_dt=self.start_dt,
            end_dt=self.end_dt,
            repeat_type='annual'
        )
        
        self.assertEqual(job.repeat_type, 'annual')
        self.assertIsNone(job.repeat_type_n_months)
    
    def test_job_creation_every_n_months(self):
        """Test creating a job with every N months repeat_type"""
        job = Job.objects.create(
            calendar=self.calendar,
            customer=self.customer,
            trailer=self.trailer,
            start_dt=self.start_dt,
            end_dt=self.end_dt,
            repeat_type='every_n_months',
            repeat_type_n_months=6
        )
        
        self.assertEqual(job.repeat_type, 'every_n_months')
        self.assertEqual(job.repeat_type_n_months, 6)
    
    def test_job_properties(self):
        """Test job properties"""
        job = Job.objects.create(
            calendar=self.calendar,
            customer=self.customer,
            trailer=self.trailer,
            start_dt=self.start_dt,
            end_dt=self.end_dt,
            repair_notes="Test repair notes",
            quote_text="Test quote text",
            trailer_color_overwrite="#FF0000"
        )
        
        # Test contact_info property
        contact_info = job.contact_info
        self.assertEqual(contact_info['name'], "John Doe")
        self.assertEqual(contact_info['phone'], "555-123-4567")
        self.assertEqual(contact_info['business'], "Test Company")
        
        # Test address_info property
        address_info = job.address_info
        self.assertEqual(address_info['line1'], "")
        self.assertEqual(address_info['city'], "")
        
        # Test calendar_color property
        self.assertEqual(job.calendar_color, "#FF0000")  # Override color
        
        # Test duration_hours property
        self.assertEqual(job.duration_hours, 2.0)
        
        # Test is_overdue property
        self.assertFalse(job.is_overdue)
        
        # Test is_today property
        self.assertFalse(job.is_today)
    
    def test_job_properties_with_customer_address(self):
        """Test job properties with customer address"""
        customer_with_address = Customer.objects.create(
            business_name="Address Company",
            contact_name="Address Contact",
            phone="555-111-2222",
            address_line1="456 Customer St",
            address_line2="Suite 100",
            city="Customer City",
            state="TX",
            postal_code="75001"
        )
        
        job = Job.objects.create(
            calendar=self.calendar,
            customer=customer_with_address,
            trailer=self.trailer,
            start_dt=self.start_dt,
            end_dt=self.end_dt
        )
        
        # Test address_info property with customer address
        address_info = job.address_info
        self.assertEqual(address_info['line1'], "456 Customer St")
        self.assertEqual(address_info['line2'], "Suite 100")
        self.assertEqual(address_info['city'], "Customer City")
        self.assertEqual(address_info['state'], "TX")
        self.assertEqual(address_info['postal_code'], "75001")
        
        # Test full_address property
        self.assertEqual(job.full_address, "456 Customer St, Suite 100, Customer City, TX, 75001")
    
    def test_job_validation_dates(self):
        """Test job date validation"""
        # Test end date before start date
        job = Job(
            calendar=self.calendar,
            customer=self.customer,
            trailer=self.trailer,
            start_dt=self.end_dt,  # Start after end
            end_dt=self.start_dt
        )
        
        with self.assertRaises(ValidationError):
            job.full_clean()
    
    def test_job_validation_repeat_type_settings(self):
        """Test job repeat_type settings validation"""
        # Test every_n_months without n_months
        job = Job(
            calendar=self.calendar,
            customer=self.customer,
            trailer=self.trailer,
            start_dt=self.start_dt,
            end_dt=self.end_dt,
            repeat_type='every_n_months',
            repeat_type_n_months=None
        )
        
        with self.assertRaises(ValidationError):
            job.full_clean()
        
        # Test every_n_months with zero
        job = Job(
            calendar=self.calendar,
            customer=self.customer,
            trailer=self.trailer,
            start_dt=self.start_dt,
            end_dt=self.end_dt,
            repeat_type='every_n_months',
            repeat_type_n_months=0
        )
        
        with self.assertRaises(ValidationError):
            job.full_clean()
    
    def test_job_validation_color_override(self):
        """Test job color override validation"""
        # Test invalid color format
        job = Job(
            calendar=self.calendar,
            customer=self.customer,
            trailer=self.trailer,
            start_dt=self.start_dt,
            end_dt=self.end_dt,
            trailer_color_overwrite="invalid_color"
        )
        
        with self.assertRaises(ValidationError):
            job.full_clean()
        
        # Test valid color format
        job = Job(
            calendar=self.calendar,
            customer=self.customer,
            trailer=self.trailer,
            start_dt=self.start_dt,
            end_dt=self.end_dt,
            trailer_color_overwrite="#FF0000"
        )
        
        job.full_clean()  # Should not raise error
    
    def test_job_validation_required_fields(self):
        """Test job required fields validation"""
        # Test missing customer
        job = Job(
            calendar=self.calendar,
            trailer=self.trailer,
            start_dt=self.start_dt,
            end_dt=self.end_dt
        )
        
        with self.assertRaises(ValidationError):
            job.full_clean()
        
        # Test missing trailer
        job = Job(
            calendar=self.calendar,
            customer=self.customer,
            start_dt=self.start_dt,
            end_dt=self.end_dt
        )
        
        with self.assertRaises(ValidationError):
            job.full_clean()
    
    def test_job_overdue_status(self):
        """Test job overdue status"""
        # Create a job that's already overdue
        past_start = timezone.now() - timedelta(hours=3)
        past_end = timezone.now() - timedelta(hours=1)
        
        job = Job.objects.create(
            calendar=self.calendar,
            customer=self.customer,
            trailer=self.trailer,
            start_dt=past_start,
            end_dt=past_end,
            status='scheduled'
        )
        
        self.assertTrue(job.is_overdue)
        
        # Completed jobs should not be overdue
        job.status = 'completed'
        job.save()
        self.assertFalse(job.is_overdue)
    
    def test_job_today_status(self):
        """Test job today status"""
        today = timezone.now().date()
        today_start = timezone.make_aware(datetime.combine(today, datetime.min.time()))
        today_end = today_start + timedelta(hours=2)
        
        job = Job.objects.create(
            calendar=self.calendar,
            customer=self.customer,
            trailer=self.trailer,
            start_dt=today_start,
            end_dt=today_end
        )
        
        self.assertTrue(job.is_today)
    
    def test_job_string_representation(self):
        """Test job string representation"""
        job = Job.objects.create(
            calendar=self.calendar,
            customer=self.customer,
            trailer=self.trailer,
            start_dt=self.start_dt,
            end_dt=self.end_dt,
            status='in_progress'
        )
        
        expected = "Test Company - T001 - Test Model (In Progress)"
        self.assertEqual(str(job), expected)
    
    def test_job_with_user_tracking(self):
        """Test job with user tracking"""
        job = Job.objects.create(
            calendar=self.calendar,
            customer=self.customer,
            trailer=self.trailer,
            start_dt=self.start_dt,
            end_dt=self.end_dt,
            created_by=self.user,
            updated_by=self.user
        )
        
        self.assertEqual(job.created_by, self.user)
        self.assertEqual(job.updated_by, self.user)
    
    def test_job_meta_ordering(self):
        """Test job meta ordering"""
        # Create jobs with different start dates
        job1 = Job.objects.create(
            calendar=self.calendar,
            customer=self.customer,
            trailer=self.trailer,
            start_dt=self.start_dt,
            end_dt=self.end_dt
        )
        
        job2 = Job.objects.create(
            calendar=self.calendar,
            customer=self.customer,
            trailer=self.trailer,
            start_dt=self.start_dt + timedelta(days=1),
            end_dt=self.end_dt + timedelta(days=1)
        )
        
        jobs = Job.objects.all()
        self.assertEqual(jobs[0], job2)  # Newest first
        self.assertEqual(jobs[1], job1)
    
    def test_job_soft_delete(self):
        """Test job soft delete functionality"""
        job = Job.objects.create(
            calendar=self.calendar,
            customer=self.customer,
            trailer=self.trailer,
            start_dt=self.start_dt,
            end_dt=self.end_dt
        )
        
        self.assertFalse(job.is_deleted)
        
        # Soft delete
        job.is_deleted = True
        job.save()
        
        # Should not appear in normal queries
        self.assertNotIn(job, Job.objects.all())
        
        # Should appear when explicitly including deleted
        self.assertIn(job, Job.objects.filter(is_deleted=True))

