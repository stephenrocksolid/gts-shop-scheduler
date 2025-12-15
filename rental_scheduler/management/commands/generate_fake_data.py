"""
Management command to generate realistic fake data for GTS Shop Scheduler.
Creates calendars, jobs, work orders, invoices, and call reminders with
comprehensive edge case coverage.
"""
import random
from datetime import datetime, timedelta, date
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from django.contrib.auth import get_user_model

from rental_scheduler.models import (
    Calendar, Job, WorkOrder, WorkOrderLine,
    Invoice, InvoiceLine, CallReminder
)

User = get_user_model()


# =============================================================================
# REALISTIC DATA POOLS
# =============================================================================

CALENDAR_DATA = [
    {"name": "Main Shop", "color": "#3B82F6", "call_reminder_color": "#F59E0B"},
    {"name": "Mobile Unit A", "color": "#10B981", "call_reminder_color": "#FBBF24"},
    {"name": "Mobile Unit B", "color": "#8B5CF6", "call_reminder_color": "#F97316"},
    {"name": "Mobile Unit C", "color": "#EC4899", "call_reminder_color": "#EF4444"},
    {"name": "Weekend Crew", "color": "#F59E0B", "call_reminder_color": "#84CC16"},
    {"name": "Emergency Service", "color": "#EF4444", "call_reminder_color": "#06B6D4"},
    {"name": "Paint & Body", "color": "#06B6D4", "call_reminder_color": "#D946EF"},
    {"name": "Welding Bay", "color": "#84CC16", "call_reminder_color": "#F43F5E"},
    {"name": "Inspection Station", "color": "#6366F1", "call_reminder_color": "#14B8A6"},
    {"name": "Off-Site Repairs", "color": "#D946EF", "call_reminder_color": "#8B5CF6"},
]

BUSINESS_NAMES = [
    "Swift Transport LLC", "Blue Ridge Trucking", "Midwest Haulers Inc",
    "Pacific Coast Logistics", "Eagle Express Freight", "Summit Moving Co",
    "Iron Horse Transport", "Delta Construction", "Pioneer Trucking",
    "Heartland Carriers", "Rocky Mountain Movers", "Great Plains Freight",
    "Coastal Shipping Co", "Liberty Logistics", "Thunder Road Transport",
    "Valley Construction", "Metro Moving Services", "Interstate Hauling",
    "Granite State Trucking", "Lone Star Freight", "Northern Logistics",
    "Sunset Carriers", "Heritage Transport", "Crossroads Trucking",
    "Apex Freight Solutions", "Cornerstone Moving", "Titan Transport",
    "Atlas Logistics", "Keystone Haulers", "Cardinal Transport Co",
    "Cascade Construction", "Phoenix Freight", "Majestic Movers",
    "Sterling Transport", "Pinnacle Trucking", "Horizon Carriers",
    "Crown Moving Co", "Elite Express", "Frontier Freight",
    "Guardian Logistics", "Nationwide Hauling", "Prime Time Transport",
]

FIRST_NAMES = [
    "James", "John", "Robert", "Michael", "William", "David", "Richard",
    "Joseph", "Thomas", "Christopher", "Mary", "Patricia", "Jennifer",
    "Linda", "Barbara", "Elizabeth", "Susan", "Jessica", "Sarah", "Karen",
    "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven", "Paul",
    "Andrew", "Joshua", "Kenneth", "Nancy", "Betty", "Margaret", "Sandra",
    "Ashley", "Kimberly", "Emily", "Donna", "Michelle", "Dorothy",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
    "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
]

STREET_NAMES = [
    "Main St", "Oak Ave", "Maple Dr", "Cedar Ln", "Pine Rd", "Elm St",
    "Washington Blvd", "Park Ave", "Lake Dr", "River Rd", "Hill St",
    "Valley View Rd", "Sunrise Blvd", "Sunset Dr", "Mountain View Ave",
    "Industrial Pkwy", "Commerce Dr", "Enterprise Blvd", "Freight Way",
    "Trucking Ln", "Highway 66", "Interstate Dr", "Logistics Way",
]

CITIES_STATES = [
    ("Houston", "TX"), ("Dallas", "TX"), ("Austin", "TX"), ("San Antonio", "TX"),
    ("Phoenix", "AZ"), ("Tucson", "AZ"), ("Denver", "CO"), ("Colorado Springs", "CO"),
    ("Los Angeles", "CA"), ("San Diego", "CA"), ("Sacramento", "CA"),
    ("Portland", "OR"), ("Seattle", "WA"), ("Salt Lake City", "UT"),
    ("Las Vegas", "NV"), ("Albuquerque", "NM"), ("Oklahoma City", "OK"),
    ("Kansas City", "MO"), ("St. Louis", "MO"), ("Memphis", "TN"),
    ("Nashville", "TN"), ("Atlanta", "GA"), ("Jacksonville", "FL"),
    ("Tampa", "FL"), ("Miami", "FL"), ("Charlotte", "NC"), ("Raleigh", "NC"),
]

TRAILER_COLORS = [
    "White", "Black", "Silver", "Gray", "Red", "Blue", "Green", "Yellow",
    "Orange", "Brown", "Beige", "Navy Blue", "Dark Green", "Maroon",
    "Cream", "Tan", "Light Blue", "Dark Gray", "Burgundy", "Forest Green",
]

TRAILER_TYPES = [
    "53' Dry Van", "48' Flatbed", "40' Reefer", "28' Pup Trailer",
    "53' Reefer", "48' Step Deck", "40' Container Chassis", "20' Box Trailer",
    "Enclosed Cargo", "Utility Trailer", "Dump Trailer", "Lowboy",
    "Drop Deck", "Tanker", "Livestock", "Car Hauler", "Equipment Trailer",
]

REPAIR_TYPES = [
    "Axle repair - worn bearings",
    "Brake system overhaul",
    "Floor replacement - rotted wood",
    "Door hinge replacement",
    "Electrical system repair - lights not working",
    "Roof patch - leak repair",
    "Landing gear replacement",
    "Tire mount and balance",
    "Mud flap installation",
    "DOT inspection and certification",
    "Air line repair",
    "Suspension repair",
    "Side panel replacement",
    "Rear door seal replacement",
    "Fifth wheel plate repair",
    "Frame welding - crack repair",
    "Refrigeration unit service",
    "Roll-up door track repair",
    "ABS sensor replacement",
    "Gladhand replacement",
    "Kingpin repair",
    "Cross member replacement",
    "Lighting upgrade to LED",
    "Reflective tape replacement",
    "Complete trailer refurbishment",
]

WORK_ORDER_ITEMS = [
    {"code": "LABOR-STD", "description": "Standard Labor", "rate": 85.00},
    {"code": "LABOR-WELD", "description": "Welding Labor", "rate": 95.00},
    {"code": "LABOR-ELEC", "description": "Electrical Labor", "rate": 90.00},
    {"code": "LABOR-REF", "description": "Refrigeration Labor", "rate": 110.00},
    {"code": "PART-BRK01", "description": "Brake Shoes (set of 4)", "rate": 245.00},
    {"code": "PART-BRK02", "description": "Brake Drums", "rate": 185.00},
    {"code": "PART-BRK03", "description": "Brake Chamber", "rate": 125.00},
    {"code": "PART-AXL01", "description": "Wheel Bearing Kit", "rate": 89.00},
    {"code": "PART-AXL02", "description": "Hub Seal", "rate": 35.00},
    {"code": "PART-LGT01", "description": "LED Tail Light Assembly", "rate": 65.00},
    {"code": "PART-LGT02", "description": "Marker Light Kit", "rate": 45.00},
    {"code": "PART-LGT03", "description": "Wiring Harness", "rate": 175.00},
    {"code": "PART-DR01", "description": "Door Hinge (heavy duty)", "rate": 95.00},
    {"code": "PART-DR02", "description": "Door Seal Kit", "rate": 120.00},
    {"code": "PART-DR03", "description": "Roll-up Door Spring", "rate": 155.00},
    {"code": "PART-FLR01", "description": "Floor Board (per sheet)", "rate": 85.00},
    {"code": "PART-FLR02", "description": "Floor Cross Member", "rate": 145.00},
    {"code": "PART-LND01", "description": "Landing Gear Assembly", "rate": 425.00},
    {"code": "PART-AIR01", "description": "Air Line Kit", "rate": 55.00},
    {"code": "PART-AIR02", "description": "Gladhand Assembly", "rate": 38.00},
    {"code": "PART-SUS01", "description": "Suspension Bushing Kit", "rate": 165.00},
    {"code": "PART-SUS02", "description": "Shock Absorber", "rate": 95.00},
    {"code": "PART-TIR01", "description": "Tire Mount & Balance", "rate": 45.00},
    {"code": "PART-MUD01", "description": "Mud Flap Set", "rate": 55.00},
    {"code": "INSP-DOT", "description": "DOT Annual Inspection", "rate": 150.00},
    {"code": "MISC-SHOP", "description": "Shop Supplies", "rate": 25.00},
    {"code": "MISC-DISP", "description": "Disposal Fee", "rate": 35.00},
]

HEX_COLORS = [
    "#EF4444", "#F97316", "#F59E0B", "#EAB308", "#84CC16",
    "#22C55E", "#10B981", "#14B8A6", "#06B6D4", "#0EA5E9",
    "#3B82F6", "#6366F1", "#8B5CF6", "#A855F7", "#D946EF",
    "#EC4899", "#F43F5E",
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def generate_phone():
    """Generate a realistic US phone number."""
    area = random.randint(200, 999)
    prefix = random.randint(200, 999)
    line = random.randint(1000, 9999)
    formats = [
        f"({area}) {prefix}-{line}",
        f"{area}-{prefix}-{line}",
        f"{area}.{prefix}.{line}",
        f"{area}{prefix}{line}",
    ]
    return random.choice(formats)


def generate_address():
    """Generate a realistic US address."""
    number = random.randint(100, 9999)
    street = random.choice(STREET_NAMES)
    city, state = random.choice(CITIES_STATES)
    zip_code = f"{random.randint(10000, 99999)}"
    
    # Sometimes include suite/unit
    line2 = ""
    if random.random() < 0.2:
        line2 = f"Suite {random.randint(100, 999)}"
    elif random.random() < 0.1:
        line2 = f"Unit {random.choice('ABCDEFGH')}"
    
    return {
        "line1": f"{number} {street}",
        "line2": line2,
        "city": city,
        "state": state,
        "postal_code": zip_code,
    }


def generate_serial():
    """Generate a trailer serial number."""
    prefix = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=random.randint(2, 4)))
    numbers = ''.join(random.choices('0123456789', k=random.randint(6, 10)))
    return f"{prefix}{numbers}"


def get_next_sunday(from_date):
    """Get the next Sunday from a given date."""
    days_until_sunday = (6 - from_date.weekday()) % 7
    if days_until_sunday == 0:
        days_until_sunday = 7
    return from_date + timedelta(days=days_until_sunday)


class Command(BaseCommand):
    help = 'Generate realistic fake data for the GTS Shop Scheduler'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before generating new data',
        )
        parser.add_argument(
            '--jobs',
            type=int,
            default=150,
            help='Number of jobs to generate (default: 150)',
        )
        parser.add_argument(
            '--calendars',
            type=int,
            default=10,
            help='Number of calendars to generate (default: 10)',
        )

    def handle(self, *args, **options):
        start_time = timezone.now()
        
        self.stdout.write(self.style.NOTICE('\n' + '='*60))
        self.stdout.write(self.style.NOTICE('GTS Shop Scheduler - Fake Data Generator'))
        self.stdout.write(self.style.NOTICE('='*60 + '\n'))
        
        if options['clear']:
            self.clear_data()
        
        # Generate data
        calendars = self.generate_calendars(options['calendars'])
        jobs = self.generate_jobs(calendars, options['jobs'])
        work_orders = self.generate_work_orders(jobs)
        invoices = self.generate_invoices(jobs, work_orders)
        reminders = self.generate_call_reminders(calendars, jobs)
        
        # Summary
        elapsed = (timezone.now() - start_time).total_seconds()
        self.print_summary(calendars, jobs, work_orders, invoices, reminders, elapsed)

    def clear_data(self):
        """Clear existing data from the database."""
        self.stdout.write(self.style.WARNING('Clearing existing data...'))
        
        with transaction.atomic():
            InvoiceLine.objects.all().delete()
            Invoice.objects.all().delete()
            WorkOrderLine.objects.all().delete()
            WorkOrder.objects.all().delete()
            CallReminder.objects.all().delete()
            Job.objects.all().delete()
            Calendar.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS('  Data cleared successfully.\n'))

    def generate_calendars(self, count):
        """Generate calendar entries."""
        self.stdout.write(self.style.NOTICE(f'Generating {count} calendars...'))
        
        calendars = []
        calendar_data = CALENDAR_DATA[:count]
        
        # If we need more calendars than predefined, generate extra
        while len(calendar_data) < count:
            i = len(calendar_data) + 1
            calendar_data.append({
                "name": f"Workshop {i}",
                "color": random.choice(HEX_COLORS),
                "call_reminder_color": random.choice(HEX_COLORS),
            })
        
        with transaction.atomic():
            for data in calendar_data:
                # Check if calendar already exists
                cal, created = Calendar.objects.get_or_create(
                    name=data["name"],
                    defaults={
                        "color": data["color"],
                        "call_reminder_color": data["call_reminder_color"],
                        "is_active": True,
                    }
                )
                calendars.append(cal)
                status = "created" if created else "exists"
                self.stdout.write(f'  - {cal.name} ({status})')
        
        self.stdout.write(self.style.SUCCESS(f'  {len(calendars)} calendars ready.\n'))
        return calendars

    def generate_jobs(self, calendars, count):
        """Generate job entries with various scenarios."""
        self.stdout.write(self.style.NOTICE(f'Generating {count} jobs...'))
        
        jobs = []
        now = timezone.now()
        today = now.date()
        
        # Status distribution
        statuses = (
            ['uncompleted'] * 40 +
            ['completed'] * 35 +
            ['pending'] * 15 +
            ['canceled'] * 10
        )
        
        # Track counts for edge cases
        all_day_count = 0
        call_reminder_count = 0
        recurring_count = 0
        overdue_count = 0
        color_override_count = 0
        
        # Track used business/contact combinations for same-day scenario
        same_day_dates = []
        
        with transaction.atomic():
            for i in range(count):
                # Pick calendar and status
                calendar = random.choice(calendars)
                status = random.choice(statuses)
                
                # Determine date range category
                date_category = random.choices(
                    ['past', 'current', 'future'],
                    weights=[20, 30, 50]
                )[0]
                
                # Generate start datetime
                if date_category == 'past':
                    days_ago = random.randint(1, 60)
                    start_date = today - timedelta(days=days_ago)
                elif date_category == 'current':
                    days_offset = random.randint(-3, 3)
                    start_date = today + timedelta(days=days_offset)
                else:  # future
                    days_ahead = random.randint(1, 90)
                    start_date = today + timedelta(days=days_ahead)
                
                # Determine if all-day event (~10%)
                is_all_day = random.random() < 0.10 and all_day_count < 15
                if is_all_day:
                    all_day_count += 1
                
                # Generate times
                if is_all_day:
                    start_dt = timezone.make_aware(
                        datetime.combine(start_date, datetime.min.time())
                    )
                    # All-day can span multiple days
                    end_days = random.randint(0, 3)
                    end_dt = timezone.make_aware(
                        datetime.combine(start_date + timedelta(days=end_days), datetime.min.time())
                    )
                else:
                    # Working hours: 7am - 6pm
                    start_hour = random.randint(7, 16)
                    start_minute = random.choice([0, 15, 30, 45])
                    start_dt = timezone.make_aware(
                        datetime.combine(start_date, datetime.min.time().replace(
                            hour=start_hour, minute=start_minute
                        ))
                    )
                    
                    # Duration: 1-8 hours
                    duration_hours = random.randint(1, 8)
                    end_dt = start_dt + timedelta(hours=duration_hours)
                
                # Create overdue scenario (~7%)
                is_overdue = (
                    random.random() < 0.07 and
                    overdue_count < 10 and
                    status == 'uncompleted'
                )
                if is_overdue:
                    overdue_count += 1
                    # Move to past
                    days_ago = random.randint(1, 14)
                    start_dt = start_dt - timedelta(days=days_ago + 7)
                    end_dt = end_dt - timedelta(days=days_ago + 7)
                
                # Generate business info
                has_business = random.random() < 0.75
                business_name = random.choice(BUSINESS_NAMES) if has_business else ""
                
                # Contact info
                has_contact = random.random() < 0.85
                contact_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}" if has_contact else ""
                
                # Phone (sometimes missing)
                has_phone = random.random() < 0.90
                phone = generate_phone() if has_phone else ""
                
                # Address (sometimes partial or missing)
                has_address = random.random() < 0.80
                address = generate_address() if has_address else None
                
                # Trailer info
                trailer_color = random.choice(TRAILER_COLORS)
                trailer_serial = generate_serial() if random.random() < 0.85 else ""
                trailer_details = random.choice(TRAILER_TYPES) if random.random() < 0.80 else ""
                
                # Repair notes
                num_repairs = random.randint(1, 3)
                repair_notes = "\n".join(random.sample(REPAIR_TYPES, num_repairs))
                
                # General notes (sometimes empty)
                notes = ""
                if random.random() < 0.5:
                    notes_options = [
                        "Customer will drop off trailer day before.",
                        "Need to order parts first.",
                        "Recurring maintenance customer.",
                        "Fleet vehicle - bill to corporate office.",
                        "Customer requests photos before/after.",
                        "Previous repair warranty claim.",
                        "Rush job - customer waiting.",
                        "Customer will pick up after 5pm.",
                        "Call customer when complete.",
                        "Insurance claim - document everything.",
                    ]
                    notes = random.choice(notes_options)
                
                # Quote (sometimes has one)
                quote = ""
                if status in ['pending', 'uncompleted'] and random.random() < 0.6:
                    quote_amount = random.randint(3, 50) * 100  # $300 - $5000
                    quote = f"${quote_amount:,}"
                
                # Color override (~10%)
                trailer_color_overwrite = ""
                if random.random() < 0.10 and color_override_count < 15:
                    color_override_count += 1
                    trailer_color_overwrite = random.choice(HEX_COLORS)
                
                # Call reminder (~20%)
                has_call_reminder = random.random() < 0.20 and call_reminder_count < 30
                call_reminder_weeks = None
                call_reminder_completed = False
                if has_call_reminder:
                    call_reminder_count += 1
                    call_reminder_weeks = random.choice([2, 3])
                    # Past jobs with reminders are likely completed
                    if date_category == 'past':
                        call_reminder_completed = random.random() < 0.8
                
                # Recurring job setup (~7% are recurring parents)
                recurrence_rule = None
                repeat_type = 'none'
                if random.random() < 0.07 and recurring_count < 10:
                    recurring_count += 1
                    repeat_type = random.choice(['monthly', 'yearly'])
                    interval = random.randint(1, 3) if repeat_type == 'monthly' else 1
                    recurrence_rule = {
                        'type': repeat_type,
                        'interval': interval,
                        'count': random.randint(6, 12),
                        'until_date': None,
                    }
                
                # Date call received (for some jobs)
                date_call_received = None
                if random.random() < 0.7:
                    days_before = random.randint(1, 14)
                    date_call_received = start_dt - timedelta(days=days_before)
                
                # Create job (bypass model save validation to avoid issues)
                job = Job(
                    calendar=calendar,
                    status=status,
                    business_name=business_name,
                    contact_name=contact_name,
                    phone=phone,
                    address_line1=address["line1"] if address else "",
                    address_line2=address["line2"] if address else "",
                    city=address["city"] if address else "",
                    state=address["state"] if address else "",
                    postal_code=address["postal_code"] if address else "",
                    date_call_received=date_call_received,
                    start_dt=start_dt,
                    end_dt=end_dt,
                    all_day=is_all_day,
                    has_call_reminder=has_call_reminder,
                    call_reminder_weeks_prior=call_reminder_weeks,
                    call_reminder_completed=call_reminder_completed,
                    repeat_type=repeat_type,
                    recurrence_rule=recurrence_rule,
                    notes=notes,
                    repair_notes=repair_notes,
                    trailer_color=trailer_color,
                    trailer_serial=trailer_serial,
                    trailer_details=trailer_details,
                    quote=quote,
                    trailer_color_overwrite=trailer_color_overwrite,
                    is_deleted=False,
                )
                job.save()
                jobs.append(job)
                
                # Progress indicator
                if (i + 1) % 25 == 0:
                    self.stdout.write(f'  Created {i + 1}/{count} jobs...')
        
        # Print job statistics
        status_counts = {}
        for job in jobs:
            status_counts[job.status] = status_counts.get(job.status, 0) + 1
        
        self.stdout.write(self.style.SUCCESS(f'  {len(jobs)} jobs created:'))
        for status, cnt in sorted(status_counts.items()):
            self.stdout.write(f'    - {status}: {cnt}')
        self.stdout.write(f'    - All-day events: {all_day_count}')
        self.stdout.write(f'    - With call reminders: {call_reminder_count}')
        self.stdout.write(f'    - Recurring parents: {recurring_count}')
        self.stdout.write(f'    - Overdue: {overdue_count}')
        self.stdout.write(f'    - Custom colors: {color_override_count}\n')
        
        return jobs

    def generate_work_orders(self, jobs):
        """Generate work orders for some jobs."""
        # Select ~25% of completed/uncompleted jobs
        eligible_jobs = [j for j in jobs if j.status in ['completed', 'uncompleted']]
        selected_jobs = random.sample(eligible_jobs, min(len(eligible_jobs), int(len(eligible_jobs) * 0.25)))
        
        self.stdout.write(self.style.NOTICE(f'Generating {len(selected_jobs)} work orders...'))
        
        work_orders = []
        
        # Find the highest existing WO number to continue from
        existing_wos = WorkOrder.objects.filter(wo_number__startswith='WO-2024-')
        wo_counter = 1
        if existing_wos.exists():
            # Extract numbers from existing WO numbers and find max
            for wo in existing_wos:
                try:
                    num = int(wo.wo_number.split('-')[-1])
                    wo_counter = max(wo_counter, num + 1)
                except (ValueError, IndexError):
                    pass
        
        with transaction.atomic():
            for job in selected_jobs:
                # Check if job already has a work order
                if hasattr(job, 'work_order'):
                    continue
                
                wo_number = f"WO-2024-{wo_counter:03d}"
                wo_counter += 1
                
                # Work order date is around job start
                wo_date = job.start_dt.date() - timedelta(days=random.randint(0, 3))
                
                work_order = WorkOrder.objects.create(
                    job=job,
                    wo_number=wo_number,
                    wo_date=wo_date,
                    notes=f"Work order for {job.display_name}" if random.random() < 0.5 else "",
                )
                
                # Add 2-5 line items
                num_lines = random.randint(2, 5)
                selected_items = random.sample(WORK_ORDER_ITEMS, num_lines)
                
                for item in selected_items:
                    qty = Decimal(str(random.randint(1, 4)))
                    if 'LABOR' in item['code']:
                        qty = Decimal(str(random.uniform(0.5, 8.0))).quantize(Decimal('0.01'))
                    
                    rate = Decimal(str(item['rate'])).quantize(Decimal('0.01'))
                    total = (qty * rate).quantize(Decimal('0.01'))
                    
                    WorkOrderLine.objects.create(
                        work_order=work_order,
                        item_code=item['code'],
                        description=item['description'],
                        qty=qty,
                        rate=rate,
                        total=total,
                    )
                
                work_orders.append(work_order)
        
        self.stdout.write(self.style.SUCCESS(f'  {len(work_orders)} work orders created.\n'))
        return work_orders

    def generate_invoices(self, jobs, work_orders):
        """Generate invoices for completed jobs."""
        # Select ~20% of completed jobs
        completed_jobs = [j for j in jobs if j.status == 'completed']
        num_invoices = min(len(completed_jobs), int(len(completed_jobs) * 0.6))
        selected_jobs = random.sample(completed_jobs, num_invoices)
        
        self.stdout.write(self.style.NOTICE(f'Generating {len(selected_jobs)} invoices...'))
        
        invoices = []
        
        # Find the highest existing invoice number to continue from
        existing_invs = Invoice.objects.filter(invoice_number__startswith='INV-2024-')
        inv_counter = 1
        if existing_invs.exists():
            for inv in existing_invs:
                try:
                    num = int(inv.invoice_number.split('-')[-1])
                    inv_counter = max(inv_counter, num + 1)
                except (ValueError, IndexError):
                    pass
        
        # Map jobs to work orders
        job_to_wo = {wo.job_id: wo for wo in work_orders}
        
        # Get or create a system user for invoice creation
        system_user, _ = User.objects.get_or_create(
            username='system',
            defaults={'is_active': False, 'email': 'system@example.com'}
        )
        
        with transaction.atomic():
            for job in selected_jobs:
                inv_number = f"INV-2024-{inv_counter:03d}"
                inv_counter += 1
                
                # Invoice date is around job end or after
                inv_date = job.end_dt.date() + timedelta(days=random.randint(0, 7))
                
                # Link to work order if exists
                work_order = job_to_wo.get(job.id)
                
                # Tax rate (Texas 8.25%)
                tax_rate = Decimal('0.0825')
                
                invoice = Invoice.objects.create(
                    job=job,
                    work_order=work_order,
                    invoice_number=inv_number,
                    invoice_date=inv_date,
                    bill_to_name=job.business_name or job.contact_name,
                    bill_to_address_line1=job.address_line1,
                    bill_to_address_line2=job.address_line2,
                    bill_to_city=job.city,
                    bill_to_state=job.state,
                    bill_to_postal_code=job.postal_code,
                    bill_to_phone=job.phone,
                    notes_public="Thank you for your business!" if random.random() < 0.5 else "",
                    notes_private="",
                    tax_rate=tax_rate,
                    subtotal=Decimal('0.00'),
                    tax_amount=Decimal('0.00'),
                    total_amount=Decimal('0.00'),
                    created_by=system_user,
                    updated_by=system_user,
                )
                
                # Add line items (either from WO or generate new)
                line_items_data = []
                
                if work_order:
                    # Copy from work order
                    for wo_line in work_order.lines.all():
                        line_items_data.append({
                            'item_code': wo_line.item_code,
                            'description': wo_line.description,
                            'qty': wo_line.qty,
                            'price': wo_line.rate.quantize(Decimal('0.01')),
                            'total': wo_line.total.quantize(Decimal('0.01')),
                        })
                else:
                    # Generate 2-6 new items
                    num_lines = random.randint(2, 6)
                    selected_items = random.sample(WORK_ORDER_ITEMS, num_lines)
                    
                    for item in selected_items:
                        qty = Decimal(str(random.randint(1, 4)))
                        if 'LABOR' in item['code']:
                            qty = Decimal(str(random.uniform(0.5, 8.0))).quantize(Decimal('0.01'))
                        
                        price = Decimal(str(item['rate'])).quantize(Decimal('0.01'))
                        total = (qty * price).quantize(Decimal('0.01'))
                        
                        line_items_data.append({
                            'item_code': item['code'],
                            'description': item['description'],
                            'qty': qty,
                            'price': price,
                            'total': total,
                        })
                
                # Create line objects for bulk insert (bypasses save() and auto-recalc)
                invoice_lines = [
                    InvoiceLine(
                        invoice=invoice,
                        item_code=li['item_code'],
                        description=li['description'],
                        qty=li['qty'],
                        price=li['price'],
                        total=li['total'],
                    ) for li in line_items_data
                ]
                
                # Use bulk_create to bypass the save() method's auto-recalculation
                InvoiceLine.objects.bulk_create(invoice_lines)
                
                # Calculate and update invoice totals with proper quantization
                subtotal = sum(li['total'] for li in line_items_data)
                tax_amount = (subtotal * tax_rate).quantize(Decimal('0.01'))
                total_amount = (subtotal + tax_amount).quantize(Decimal('0.01'))
                
                # Use update() to bypass Invoice.save() validation
                Invoice.objects.filter(pk=invoice.pk).update(
                    subtotal=subtotal.quantize(Decimal('0.01')),
                    tax_amount=tax_amount,
                    total_amount=total_amount
                )
                
                invoices.append(invoice)
        
        self.stdout.write(self.style.SUCCESS(f'  {len(invoices)} invoices created.\n'))
        return invoices

    def generate_call_reminders(self, calendars, jobs):
        """Generate standalone call reminders."""
        self.stdout.write(self.style.NOTICE('Generating call reminders...'))
        
        reminders = []
        today = timezone.now().date()
        
        with transaction.atomic():
            # Generate ~15 standalone reminders
            for i in range(15):
                calendar = random.choice(calendars)
                
                # Find upcoming Sundays
                reminder_date = get_next_sunday(today + timedelta(weeks=random.randint(0, 8)))
                
                notes_options = [
                    "Call to confirm appointment",
                    "Follow up on quote",
                    "Check if parts arrived",
                    "Remind about DOT inspection due",
                    "Confirm trailer drop-off time",
                    "Discuss additional repairs needed",
                    "Schedule follow-up service",
                    "Check on fleet maintenance schedule",
                    "Confirm payment received",
                    "Remind about warranty expiration",
                ]
                
                reminder = CallReminder.objects.create(
                    job=None,  # Standalone
                    calendar=calendar,
                    reminder_date=reminder_date,
                    notes=random.choice(notes_options),
                    completed=random.random() < 0.2,  # 20% completed
                )
                reminders.append(reminder)
            
            # Also create some job-linked reminders
            jobs_with_reminders = [j for j in jobs if j.has_call_reminder and j.start_dt.date() > today]
            for job in jobs_with_reminders[:10]:
                weeks_prior = job.call_reminder_weeks_prior or 2
                reminder_date = get_next_sunday(job.start_dt.date() - timedelta(weeks=weeks_prior - 1))
                
                if reminder_date >= today:
                    reminder = CallReminder.objects.create(
                        job=job,
                        calendar=job.calendar,
                        reminder_date=reminder_date,
                        notes=f"Call {job.display_name} to confirm job",
                        completed=job.call_reminder_completed,
                    )
                    reminders.append(reminder)
        
        self.stdout.write(self.style.SUCCESS(f'  {len(reminders)} call reminders created.\n'))
        return reminders

    def print_summary(self, calendars, jobs, work_orders, invoices, reminders, elapsed):
        """Print summary statistics."""
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('GENERATION COMPLETE'))
        self.stdout.write(self.style.SUCCESS('='*60))
        
        self.stdout.write(f'\n  Calendars:      {len(calendars)}')
        self.stdout.write(f'  Jobs:           {len(jobs)}')
        self.stdout.write(f'  Work Orders:    {len(work_orders)}')
        self.stdout.write(f'  Invoices:       {len(invoices)}')
        self.stdout.write(f'  Call Reminders: {len(reminders)}')
        self.stdout.write(f'\n  Time elapsed:   {elapsed:.2f} seconds')
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*60 + '\n'))
