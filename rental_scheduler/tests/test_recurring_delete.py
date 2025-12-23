"""
Tests for recurring job delete API with scope support.
"""
import json
from datetime import datetime, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from rental_scheduler.models import Job, Calendar


class RecurringDeleteAPITestCase(TestCase):
    """Test the job_delete_api_recurring endpoint with various scopes."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.calendar = Calendar.objects.create(
            name="Test Calendar",
            color="#FF0000",
            is_active=True
        )
        
        # Create a recurring parent job
        self.parent = Job.objects.create(
            business_name="Recurring Test",
            calendar=self.calendar,
            start_dt=timezone.now(),
            end_dt=timezone.now() + timedelta(hours=2),
            all_day=False,
            status='uncompleted'
        )
        
        # Add recurrence rule
        self.parent.recurrence_rule = {
            'type': 'weekly',
            'interval': 1,
            'count': 5
        }
        self.parent.save()
        
        # Create instances manually for testing
        self.instances = []
        for i in range(1, 6):  # 5 instances
            instance_start = self.parent.start_dt + timedelta(weeks=i)
            instance = Job.objects.create(
                business_name="Recurring Test",
                calendar=self.calendar,
                start_dt=instance_start,
                end_dt=instance_start + timedelta(hours=2),
                all_day=False,
                status='uncompleted',
                recurrence_parent=self.parent,
                recurrence_original_start=instance_start
            )
            self.instances.append(instance)

    def test_delete_instance_this_only(self):
        """Test deleting a single instance with this_only scope."""
        instance = self.instances[2]  # Middle instance
        url = reverse('rental_scheduler:job_delete_api_recurring', kwargs={'pk': instance.pk})
        
        response = self.client.post(
            url,
            data=json.dumps({'delete_scope': 'this_only'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted_count'], 1)
        self.assertEqual(data['scope'], 'this_only')
        
        # Verify only this instance is deleted
        instance.refresh_from_db()
        self.assertTrue(instance.is_deleted)
        
        # Verify other instances are not deleted
        for i, inst in enumerate(self.instances):
            if i != 2:
                inst.refresh_from_db()
                self.assertFalse(inst.is_deleted)
        
        # Verify parent is not deleted
        self.parent.refresh_from_db()
        self.assertFalse(self.parent.is_deleted)

    def test_delete_instance_this_and_future(self):
        """Test deleting instance and future instances with this_and_future scope."""
        instance = self.instances[2]  # Middle instance (index 2, so instances 2, 3, 4 should be deleted)
        url = reverse('rental_scheduler:job_delete_api_recurring', kwargs={'pk': instance.pk})
        
        response = self.client.post(
            url,
            data=json.dumps({'delete_scope': 'this_and_future'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted_count'], 3)  # Instances 2, 3, 4
        self.assertEqual(data['scope'], 'this_and_future')
        
        # Verify this and future instances are deleted
        for i in [2, 3, 4]:
            self.instances[i].refresh_from_db()
            self.assertTrue(self.instances[i].is_deleted)
        
        # Verify earlier instances are not deleted
        for i in [0, 1]:
            self.instances[i].refresh_from_db()
            self.assertFalse(self.instances[i].is_deleted)
        
        # Verify parent end_recurrence_date is set
        self.parent.refresh_from_db()
        self.assertIsNotNone(self.parent.end_recurrence_date)
        # Should be set to day before the deleted boundary
        expected_date = instance.recurrence_original_start.date() - timedelta(days=1)
        self.assertEqual(self.parent.end_recurrence_date, expected_date)

    def test_delete_parent_this_and_future(self):
        """Test deleting parent with this_and_future scope."""
        url = reverse('rental_scheduler:job_delete_api_recurring', kwargs={'pk': self.parent.pk})
        
        response = self.client.post(
            url,
            data=json.dumps({'delete_scope': 'this_and_future'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted_count'], 5)  # All 5 instances
        self.assertEqual(data['scope'], 'this_and_future')
        
        # Verify all instances are deleted
        for instance in self.instances:
            instance.refresh_from_db()
            self.assertTrue(instance.is_deleted)
        
        # Verify parent is NOT deleted but has end_recurrence_date set
        self.parent.refresh_from_db()
        self.assertFalse(self.parent.is_deleted)
        self.assertIsNotNone(self.parent.end_recurrence_date)
        self.assertEqual(self.parent.end_recurrence_date, self.parent.start_dt.date())

    def test_delete_all_scope(self):
        """Test deleting entire series with all scope."""
        instance = self.instances[2]
        url = reverse('rental_scheduler:job_delete_api_recurring', kwargs={'pk': instance.pk})
        
        response = self.client.post(
            url,
            data=json.dumps({'delete_scope': 'all'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted_count'], 6)  # 5 instances + 1 parent
        self.assertEqual(data['scope'], 'all')
        
        # Verify all instances are deleted
        for instance in self.instances:
            instance.refresh_from_db()
            self.assertTrue(instance.is_deleted)
        
        # Verify parent is deleted
        self.parent.refresh_from_db()
        self.assertTrue(self.parent.is_deleted)

    def test_delete_parent_this_only_rejected(self):
        """Test that deleting only the parent (with instances) is rejected."""
        url = reverse('rental_scheduler:job_delete_api_recurring', kwargs={'pk': self.parent.pk})
        
        response = self.client.post(
            url,
            data=json.dumps({'delete_scope': 'this_only'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertIn('series template', data['error'])
        
        # Verify nothing was deleted
        self.parent.refresh_from_db()
        self.assertFalse(self.parent.is_deleted)
        
        for instance in self.instances:
            instance.refresh_from_db()
            self.assertFalse(instance.is_deleted)

    def test_delete_non_recurring_job(self):
        """Test deleting a non-recurring job with recurring endpoint."""
        non_recurring = Job.objects.create(
            business_name="Non-Recurring Test",
            calendar=self.calendar,
            start_dt=timezone.now(),
            end_dt=timezone.now() + timedelta(hours=1),
            all_day=False,
            status='uncompleted'
        )
        
        url = reverse('rental_scheduler:job_delete_api_recurring', kwargs={'pk': non_recurring.pk})
        
        response = self.client.post(
            url,
            data=json.dumps({'delete_scope': 'this_only'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted_count'], 1)
        
        # Verify job is soft deleted
        non_recurring.refresh_from_db()
        self.assertTrue(non_recurring.is_deleted)

    def test_delete_already_deleted_instances(self):
        """Test that already deleted instances are not counted again."""
        # Soft delete first two instances
        self.instances[0].is_deleted = True
        self.instances[0].save()
        self.instances[1].is_deleted = True
        self.instances[1].save()
        
        # Delete from instance 1 onwards (should only count non-deleted ones)
        instance = self.instances[1]
        url = reverse('rental_scheduler:job_delete_api_recurring', kwargs={'pk': instance.pk})
        
        response = self.client.post(
            url,
            data=json.dumps({'delete_scope': 'this_and_future'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        # Should only count instances 2, 3, 4 (not 1 which was already deleted)
        self.assertEqual(data['deleted_count'], 3)

    def test_default_scope_is_this_only(self):
        """Test that missing delete_scope defaults to this_only."""
        instance = self.instances[2]
        url = reverse('rental_scheduler:job_delete_api_recurring', kwargs={'pk': instance.pk})
        
        response = self.client.post(
            url,
            data=json.dumps({}),  # No delete_scope
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['scope'], 'this_only')
        self.assertEqual(data['deleted_count'], 1)

