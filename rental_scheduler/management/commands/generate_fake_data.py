"""
Management command to generate realistic fake data for GTS Shop Scheduler.
Creates calendars, jobs, and call reminders with
comprehensive edge case coverage.
"""
import random
from datetime import datetime, timedelta, date

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from django.contrib.auth import get_user_model

from rental_scheduler.models import (
    Calendar, Job,
    CallReminder
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
        reminders = self.generate_call_reminders(calendars, jobs)
        
        elapsed = (timezone.now() - start_time).total_seconds()
        self.print_summary(calendars, jobs, reminders, elapsed)

    def clear_data(self):
        """Clear existing data from the database."""
        self.stdout.write(self.style.WARNING('Clearing existing data...'))
        
        with transaction.atomic():
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

    def print_summary(self, calendars, jobs, reminders, elapsed):
        """Print summary statistics."""
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('GENERATION COMPLETE'))
        self.stdout.write(self.style.SUCCESS('='*60))
        
        self.stdout.write(f'\n  Calendars:      {len(calendars)}')
        self.stdout.write(f'  Jobs:           {len(jobs)}')
        self.stdout.write(f'  Call Reminders: {len(reminders)}')
        self.stdout.write(f'\n  Time elapsed:   {elapsed:.2f} seconds')
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*60 + '\n'))
