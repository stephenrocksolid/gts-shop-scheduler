from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from rental_scheduler.models import Calendar, Customer, Trailer, Job, TrailerCategory


class Command(BaseCommand):
    help = 'Set up test data for the job calendar'

    def handle(self, *args, **options):
        self.stdout.write('Setting up test data...')
        
        # Create categories if they don't exist
        category, created = TrailerCategory.objects.get_or_create(
            category='Utility Trailers'
        )
        if created:
            self.stdout.write(f'Created category: {category.category}')
        
        # Create calendars
        calendars = []
        calendar_data = [
            {'name': 'Shop', 'color': '#3B82F6'},
            {'name': 'Mobile Unit A', 'color': '#16A34A'},
            {'name': 'Mobile Unit B', 'color': '#DC2626'},
        ]
        
        for cal_data in calendar_data:
            calendar, created = Calendar.objects.get_or_create(
                name=cal_data['name'],
                defaults={'color': cal_data['color'], 'is_active': True}
            )
            calendars.append(calendar)
            if created:
                self.stdout.write(f'Created calendar: {calendar.name}')
        
        # Create customers
        customers = []
        customer_data = [
            {'business_name': 'ABC Construction', 'contact_name': 'John Smith', 'phone': '+1555010101'},
            {'business_name': 'XYZ Moving', 'contact_name': 'Jane Doe', 'phone': '+1555010202'},
            {'business_name': 'City Services', 'contact_name': 'Bob Johnson', 'phone': '+1555010303'},
        ]
        
        for cust_data in customer_data:
            customer, created = Customer.objects.get_or_create(
                business_name=cust_data['business_name'],
                defaults={
                    'contact_name': cust_data['contact_name'],
                    'phone': cust_data['phone'],
                    'address_line1': '123 Main St',
                    'city': 'Anytown',
                    'state': 'CA',
                    'postal_code': '90210'
                }
            )
            customers.append(customer)
            if created:
                self.stdout.write(f'Created customer: {customer.business_name}')
        
        # Create trailers
        trailers = []
        trailer_data = [
            {'number': 'T001', 'model': 'Utility 6x12'},
            {'number': 'T002', 'model': 'Utility 6x10'},
            {'number': 'T003', 'model': 'Utility 5x8'},
        ]
        
        for trailer_data_item in trailer_data:
            trailer, created = Trailer.objects.get_or_create(
                number=trailer_data_item['number'],
                defaults={
                    'model': trailer_data_item['model'],
                    'category': category,
                    'is_available': True,
                    'length': 12,
                    'width': 6,
                    'height': 6.5,
                    'hauling_capacity': 3500.00
                }
            )
            trailers.append(trailer)
            if created:
                self.stdout.write(f'Created trailer: {trailer.number}')
        
        # Create jobs
        now = timezone.now()
        job_data = [
            {
                'calendar': calendars[0],
                'customer': customers[0],
                'trailer': trailers[0],
                'status': 'scheduled',
                'start_dt': now + timedelta(days=1, hours=9),
                'end_dt': now + timedelta(days=1, hours=17),
                'business_name': 'ABC Construction',
                'repair_notes': 'Annual maintenance and inspection'
            },
            {
                'calendar': calendars[1],
                'customer': customers[1],
                'trailer': trailers[1],
                'status': 'in_progress',
                'start_dt': now - timedelta(hours=2),
                'end_dt': now + timedelta(hours=6),
                'business_name': 'XYZ Moving',
                'repair_notes': 'Brake system repair'
            },
            {
                'calendar': calendars[2],
                'customer': customers[2],
                'trailer': trailers[2],
                'status': 'completed',
                'start_dt': now - timedelta(days=1, hours=8),
                'end_dt': now - timedelta(days=1, hours=0),
                'business_name': 'City Services',
                'repair_notes': 'Electrical system upgrade - COMPLETED'
            },
            {
                'calendar': calendars[0],
                'customer': customers[0],
                'trailer': trailers[0],
                'status': 'scheduled',
                'start_dt': now + timedelta(days=3, hours=10),
                'end_dt': now + timedelta(days=3, hours=15),
                'business_name': 'ABC Construction',
                'repair_notes': 'Tire replacement and alignment'
            },
            {
                'calendar': calendars[1],
                'customer': customers[1],
                'trailer': trailers[1],
                'status': 'canceled',
                'start_dt': now + timedelta(days=2, hours=14),
                'end_dt': now + timedelta(days=2, hours=18),
                'business_name': 'XYZ Moving',
                'repair_notes': 'CANCELED - Customer rescheduled'
            },
        ]
        
        for job_item in job_data:
            job, created = Job.objects.get_or_create(
                calendar=job_item['calendar'],
                customer=job_item['customer'],
                trailer=job_item['trailer'],
                start_dt=job_item['start_dt'],
                defaults={
                    'status': job_item['status'],
                    'end_dt': job_item['end_dt'],
                    'business_name': job_item['business_name'],
                    'repair_notes': job_item['repair_notes'],
                    'created_by': None  # Will be set to current user when created via UI
                }
            )
            if created:
                self.stdout.write(f'Created job: {job.business_name} - {job.trailer.number}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully set up test data:\n'
                f'- {len(calendars)} calendars\n'
                f'- {len(customers)} customers\n'
                f'- {len(trailers)} trailers\n'
                f'- {Job.objects.count()} jobs'
            )
        )
