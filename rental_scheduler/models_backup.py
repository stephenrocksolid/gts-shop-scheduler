from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from datetime import datetime
import uuid
import os
from django.core.files.storage import FileSystemStorage
import logging
from django.utils import timezone
import time
from decimal import Decimal
from rental_scheduler.utils.datetime import format_local
from django.db.models.signals import pre_save
from django.dispatch import receiver

# Create your models here.

logger = logging.getLogger(__name__)

class Calendar(models.Model):
    """
    Calendar model for organizing jobs and events in the trailer repair shop.
    Each calendar represents a logical grouping (e.g., "Shop", "Mobile Unit A")
    and determines color coding and filtering in the calendar view.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique name for the calendar (e.g., 'Shop', 'Mobile Unit A')"
    )
    color = models.CharField(
        max_length=7,  # CSS hex color code (#RRGGBB)
        default="#3B82F6",  # Default blue color
        help_text="CSS hex color code for calendar display (e.g., #3B82F6)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this calendar is active and visible"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Calendar"
        verbose_name_plural = "Calendars"
        ordering = ['name']

    def __str__(self):
        return self.name

    def clean(self):
        """Validate the calendar data"""
        super().clean()
        
        # Validate color format (basic hex validation)
        if self.color and not self.color.startswith('#'):
            raise ValidationError({
                'color': 'Color must be a valid CSS hex color code starting with #'
            })
        
        # Check for duplicate names (case-insensitive)
        if self.name:
            existing = Calendar.objects.filter(name__iexact=self.name)
            if self.pk:
                existing = existing.exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError({
                    'name': 'A calendar with this name already exists.'
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Job(models.Model):
    """
    Job model for managing both repair work orders and rental jobs in the trailer shop.
    This is the central model that tracks all scheduled work and customer interactions.
    """
    # Status choices for job tracking
    STATUS_CHOICES = [
        ('uncompleted', 'Uncompleted'),
        ('completed', 'Completed'),
    ]
    
    # Repeat type choices for recurring jobs
    REPEAT_CHOICES = [
        ('none', 'None'),
        ('monthly', 'Monthly'),
        ('yearly', 'Annually'),
    ]
    
    # Calendar and scheduling
    calendar = models.ForeignKey(
        Calendar,
        on_delete=models.CASCADE,
        related_name='jobs',
        help_text="Calendar this job belongs to (e.g., 'Shop', 'Mobile Unit A')"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='uncompleted',
        help_text="Current status of the job"
    )
    
    # Customer and trailer information is now stored as text fields below
    
    # Business contact information
    business_name = models.CharField(
        max_length=150,
        blank=True,
        help_text="Business or company name"
    )
    contact_name = models.CharField(
        max_length=120,
        blank=True,
        help_text="Contact person name"
    )
    phone = models.CharField(
        max_length=25,
        blank=True,
        help_text="Contact phone number"
    )
    
    # Address information
    address_line1 = models.CharField(
        max_length=200,
        blank=True,
        help_text="Street address line 1"
    )
    address_line2 = models.CharField(
        max_length=200,
        blank=True,
        help_text="Street address line 2 (apartment, suite, etc.)"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        help_text="City name"
    )
    state = models.CharField(
        max_length=2,
        blank=True,
        help_text="Two-letter state code"
    )
    postal_code = models.CharField(
        max_length=10,
        blank=True,
        help_text="ZIP or postal code"
    )
    
    # Timing and scheduling
    date_call_received = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time the initial call was received"
    )
    start_dt = models.DateTimeField(
        help_text="Start date and time of the job"
    )
    end_dt = models.DateTimeField(
        help_text="End date and time of the job"
    )
    all_day = models.BooleanField(
        default=False,
        help_text="Whether this is an all-day event"
    )
    
    # Repeat functionality
    repeat_type = models.CharField(
        max_length=40,
        choices=REPEAT_CHOICES,
        default='none',
        blank=True,
        help_text="Type of repeat for recurring jobs"
    )
    repeat_n_months = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of months between repeats (for 'Every N Months' type)"
    )
    
    # Job details
    notes = models.TextField(
        blank=True,
        help_text="General notes about the job"
    )
    repair_notes = models.TextField(
        blank=True,
        help_text="Detailed notes about the repair work needed"
    )
    
    # Trailer info fields
    trailer_color = models.CharField(
        max_length=60,
        blank=True,
        help_text="Color of the trailer"
    )
    trailer_serial = models.CharField(
        max_length=120,
        blank=True,
        help_text="Serial number of the trailer"
    )
    trailer_details = models.CharField(
        max_length=200,
        blank=True,
        help_text="Additional trailer details"
    )
    
    # Quote field
    quote = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Quote amount for the job"
    )
    trailer_color_overwrite = models.CharField(
        max_length=7,  # CSS hex color code
        blank=True,
        help_text="Override trailer color for calendar display (CSS hex code)"
    )
    quote_text = models.TextField(
        blank=True,
        help_text="Quote text for customer-facing documents"
    )
    
    # System fields
    is_deleted = models.BooleanField(
        default=False,
        help_text="Soft delete flag"
    )
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_jobs',
        help_text="User who created this job"
    )
    updated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_jobs',
        help_text="User who last updated this job"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Job"
        verbose_name_plural = "Jobs"
        ordering = ['-start_dt']
        indexes = [
            models.Index(fields=['calendar', 'status']),
            models.Index(fields=['start_dt', 'end_dt']),
            models.Index(fields=['status', 'start_dt']),
            models.Index(fields=['is_deleted']),
            models.Index(fields=['repeat_type']),
        ]
    
    def __str__(self):
        """String representation of the job"""
        customer_name = self.business_name or self.contact_name or "No Name"
        trailer_info = f"{self.trailer_color or 'Unknown'} Trailer"
        return f"{customer_name} - {trailer_info} ({self.get_status_display()})"
    
    @property
    def display_name(self):
        """Get the primary display name for the job"""
        return self.business_name or self.contact_name or "No Name"
    
    @property
    def contact_info(self):
        """Get the contact information"""
        return {
            'name': self.contact_name,
            'phone': self.phone,
            'business': self.business_name,
        }
    
    @property
    def address_info(self):
        """Get the address information"""
        return {
            'line1': self.address_line1,
            'line2': self.address_line2,
            'city': self.city,
            'state': self.state,
            'postal_code': self.postal_code,
        }
    
    @property
    def full_address(self):
        """Get the complete formatted address"""
        address_parts = []
        
        if self.address_line1:
            address_parts.append(self.address_line1)
            
        if self.address_line2:
            address_parts.append(self.address_line2)
            
        city_state_zip = []
        if self.city:
            city_state_zip.append(self.city)
            
        if self.state:
            city_state_zip.append(self.state)
            
        if self.postal_code:
            city_state_zip.append(self.postal_code)
            
        if city_state_zip:
            address_parts.append(', '.join(city_state_zip))
            
        return ', '.join(address_parts) if address_parts else None
    
    @property
    def calendar_color(self):
        """Get the color for calendar display (trailer override or calendar default)"""
        if self.trailer_color_overwrite:
            return self.trailer_color_overwrite
        return self.calendar.color
    
    @property
    def duration_hours(self):
        """Calculate the duration of the job in hours"""
        if self.all_day:
            return 24.0
        duration = self.end_dt - self.start_dt
        return duration.total_seconds() / 3600
    
    @property
    def is_overdue(self):
        """Check if the job is overdue (past end time and not completed)"""
        if self.status == 'completed':
            return False
        return self.end_dt < timezone.now()
    
    @property
    def is_today(self):
        """Check if the job is scheduled for today"""
        today = timezone.now().date()
        return self.start_dt.date() == today
    
    @property
    def display_name(self):
        """Property for display name (alias for get_display_name)"""
        return self.get_display_name()
    
    def get_display_name(self):
        """Get the display name for the job (business name or contact name)"""
        if self.business_name:
            return self.business_name
        elif self.contact_name:
            return self.contact_name
        else:
            return "No Name Provided"
    
    def get_phone(self):
        """Get the phone number for the job"""
        return self.phone
    
    def clean(self):
        """Validate the job data"""
        super().clean()
        
        # Validate dates
        if self.start_dt and self.end_dt:
            if self.start_dt >= self.end_dt:
                raise ValidationError({
                    'end_dt': 'End date must be after start date'
                })
        
        # Validate repeat settings
        if self.repeat_type == 'monthly' and self.repeat_n_months:
            if self.repeat_n_months < 1:
                raise ValidationError({
                    'repeat_n_months': 'Number of months must be greater than 0'
                })
        elif self.repeat_type == 'none':
            self.repeat_n_months = None
        
        # Validate color override
        if self.trailer_color_overwrite and not self.trailer_color_overwrite.startswith('#'):
            raise ValidationError({
                'trailer_color_overwrite': 'Color override must be a valid CSS hex color code starting with #'
            })
        
        # No customer/trailer validation needed anymore
    
    def save(self, *args, **kwargs):
        """Save the job with validation"""
        self.full_clean()
        super().save(*args, **kwargs)


class WorkOrder(models.Model):
    """
    Work Order model for tracking detailed repair work and line items.
    Each work order is associated with exactly one job and contains multiple line items.
    """
    job = models.OneToOneField(
        Job,
        on_delete=models.CASCADE,
        related_name='work_order',
        help_text="Associated job for this work order"
    )
    wo_number = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique work order number (e.g., WO-2024-001)"
    )
    wo_date = models.DateField(
        default=timezone.now,
        help_text="Date the work order was created"
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about the work order"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Work Order"
        verbose_name_plural = "Work Orders"
        ordering = ['-wo_date', '-created_at']
        indexes = [
            models.Index(fields=['wo_number']),
            models.Index(fields=['wo_date']),
            models.Index(fields=['job']),
        ]
    
    def __str__(self):
        """String representation of the work order"""
        return f"{self.wo_number} - {self.job.display_name}"
    
    @property
    def total_amount(self):
        """Calculate the total amount from all line items"""
        return sum(line.total for line in self.lines.all())
    
    @property
    def line_count(self):
        """Get the number of line items"""
        return self.lines.count()
    
    def clean(self):
        """Validate the work order data"""
        super().clean()
        
        # Validate work order number format (basic validation)
        if self.wo_number and not self.wo_number.strip():
            raise ValidationError({
                'wo_number': 'Work order number cannot be empty'
            })
    
    def save(self, *args, **kwargs):
        """Save the work order with validation"""
        self.full_clean()
        super().save(*args, **kwargs)


class WorkOrderLine(models.Model):
    """
    Work Order Line model for individual line items in a work order.
    Each line represents a specific repair task, part, or service.
    """
    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name='lines',
        help_text="Work order this line belongs to"
    )
    item_code = models.CharField(
        max_length=50,
        blank=True,
        help_text="Item code or part number"
    )
    description = models.CharField(
        max_length=200,
        help_text="Description of the work or item"
    )
    qty = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1.00,
        help_text="Quantity of the item or hours of work"
    )
    rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Rate per unit (price per item or hourly rate)"
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Total amount for this line (qty * rate)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Work Order Line"
        verbose_name_plural = "Work Order Lines"
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['work_order']),
            models.Index(fields=['item_code']),
            models.Index(fields=['description']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(qty__gte=0),
                name='work_order_line_qty_non_negative'
            ),
            models.CheckConstraint(
                check=models.Q(rate__gte=0),
                name='work_order_line_rate_non_negative'
            ),
            models.CheckConstraint(
                check=models.Q(total__gte=0),
                name='work_order_line_total_non_negative'
            ),
        ]
    
    def __str__(self):
        """String representation of the work order line"""
        return f"{self.description} - Qty: {self.qty} @ ${self.rate}"
    
    def clean(self):
        """Validate the work order line data"""
        super().clean()
        
        # Validate quantity is positive
        if self.qty and self.qty <= 0:
            raise ValidationError({
                'qty': 'Quantity must be greater than zero'
            })
        
        # Validate rate is non-negative
        if self.rate and self.rate < 0:
            raise ValidationError({
                'rate': 'Rate cannot be negative'
            })
        
        # Validate description is not empty
        if not self.description or not self.description.strip():
            raise ValidationError({
                'description': 'Description is required'
            })
    
    def save(self, *args, **kwargs):
        """Save the work order line with validation and total calculation"""
        self.full_clean()
        
        # Calculate total if not explicitly set
        if self.qty and self.rate:
            self.total = self.qty * self.rate
        
        super().save(*args, **kwargs)


class Invoice(models.Model):
    """
    Invoice model for billing customers for completed work.
    Can be linked to a job and/or work order, with proper billing information.
    """
    # Relationships
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='invoices',
        help_text="Job this invoice is for"
    )
    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
        help_text="Work order this invoice is based on (optional)"
    )
    
    # Invoice details
    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique invoice number (e.g., INV-2024-001)"
    )
    invoice_date = models.DateField(
        default=timezone.now,
        help_text="Date the invoice was created"
    )
    
    # Billing information (can override job customer info)
    bill_to_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Name to bill (overrides job customer if provided)"
    )
    bill_to_address_line1 = models.CharField(
        max_length=200,
        blank=True,
        help_text="Billing address line 1 (overrides job address if provided)"
    )
    bill_to_address_line2 = models.CharField(
        max_length=200,
        blank=True,
        help_text="Billing address line 2 (overrides job address if provided)"
    )
    bill_to_city = models.CharField(
        max_length=100,
        blank=True,
        help_text="Billing city (overrides job city if provided)"
    )
    bill_to_state = models.CharField(
        max_length=2,
        blank=True,
        help_text="Billing state (overrides job state if provided)"
    )
    bill_to_postal_code = models.CharField(
        max_length=10,
        blank=True,
        help_text="Billing postal code (overrides job postal code if provided)"
    )
    bill_to_phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Billing phone (overrides job phone if provided)"
    )
    
    # Notes
    notes_public = models.TextField(
        blank=True,
        help_text="Notes visible to customer on invoice"
    )
    notes_private = models.TextField(
        blank=True,
        help_text="Internal notes not visible to customer"
    )
    
    # Totals (calculated from line items)
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Subtotal before tax"
    )
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=Decimal('0.0000'),
        help_text="Tax rate as decimal (e.g., 0.0825 for 8.25%)"
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Tax amount"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total amount including tax"
    )
    
    # System fields
    is_deleted = models.BooleanField(
        default=False,
        help_text="Soft delete flag"
    )
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_invoices',
        help_text="User who created this invoice"
    )
    updated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='updated_invoices',
        help_text="User who last updated this invoice"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        ordering = ['-invoice_date', '-created_at']
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['invoice_date']),
            models.Index(fields=['job']),
            models.Index(fields=['work_order']),
            models.Index(fields=['is_deleted']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.invoice_number} - {self.bill_to_name or self.job.display_name}"

    def clean(self):
        """Validate the invoice data"""
        super().clean()
        
        # Validate invoice number is not empty
        if not self.invoice_number or not self.invoice_number.strip():
            raise ValidationError({
                'invoice_number': 'Invoice number is required.'
            })
        
        # Validate tax rate is non-negative
        if self.tax_rate < 0:
            raise ValidationError({
                'tax_rate': 'Tax rate cannot be negative.'
            })
        
        # Validate totals are non-negative
        if self.subtotal < 0:
            raise ValidationError({
                'subtotal': 'Subtotal cannot be negative.'
            })
        
        if self.tax_amount < 0:
            raise ValidationError({
                'tax_amount': 'Tax amount cannot be negative.'
            })
        
        if self.total_amount < 0:
            raise ValidationError({
                'total_amount': 'Total amount cannot be negative.'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def bill_to_display_name(self):
        """Get the billing name to display"""
        return self.bill_to_name or self.job.display_name

    @property
    def bill_to_address_info(self):
        """Get the billing address information"""
        if self.bill_to_address_line1:
            address_parts = [self.bill_to_address_line1]
            if self.bill_to_address_line2:
                address_parts.append(self.bill_to_address_line2)
            if self.bill_to_city and self.bill_to_state:
                address_parts.append(f"{self.bill_to_city}, {self.bill_to_state}")
            elif self.bill_to_city:
                address_parts.append(self.bill_to_city)
            elif self.bill_to_state:
                address_parts.append(self.bill_to_state)
            if self.bill_to_postal_code:
                address_parts.append(self.bill_to_postal_code)
            return " ".join(address_parts)
        return self.job.address_info

    @property
    def bill_to_full_address(self):
        """Get the complete billing address"""
        if self.bill_to_address_line1:
            address_parts = []
            if self.bill_to_name:
                address_parts.append(self.bill_to_name)
            address_parts.append(self.bill_to_address_line1)
            if self.bill_to_address_line2:
                address_parts.append(self.bill_to_address_line2)
            if self.bill_to_city and self.bill_to_state:
                address_parts.append(f"{self.bill_to_city}, {self.bill_to_state}")
            elif self.bill_to_city:
                address_parts.append(self.bill_to_city)
            elif self.bill_to_state:
                address_parts.append(self.bill_to_state)
            if self.bill_to_postal_code:
                address_parts.append(self.bill_to_postal_code)
            if self.bill_to_phone:
                address_parts.append(self.bill_to_phone)
            return "\n".join(address_parts)
        return self.job.full_address

    @property
    def line_count(self):
        """Get the number of line items"""
        return self.lines.count()

    def calculate_totals(self):
        """Calculate subtotal, tax, and total from line items"""
        subtotal = sum(line.total for line in self.lines.all())
        tax_amount = subtotal * self.tax_rate
        total_amount = subtotal + tax_amount
        
        self.subtotal = subtotal
        self.tax_amount = tax_amount
        self.total_amount = total_amount


class InvoiceLine(models.Model):
    """
    InvoiceLine model for individual line items on an invoice.
    Each line represents a specific item or service being billed.
    """
    # Relationship
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='lines',
        help_text="Invoice this line belongs to"
    )
    
    # Line item details
    item_code = models.CharField(
        max_length=50,
        blank=True,
        help_text="Item code or SKU"
    )
    description = models.CharField(
        max_length=255,
        help_text="Description of the item or service"
    )
    qty = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Quantity"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Unit price"
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Line total (qty * price)"
    )
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Invoice Line"
        verbose_name_plural = "Invoice Lines"
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['invoice']),
            models.Index(fields=['item_code']),
            models.Index(fields=['created_at']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(qty__gt=0),
                name='invoice_line_positive_qty'
            ),
            models.CheckConstraint(
                check=models.Q(price__gte=0),
                name='invoice_line_non_negative_price'
            ),
            models.CheckConstraint(
                check=models.Q(total__gte=0),
                name='invoice_line_non_negative_total'
            ),
        ]

    def __str__(self):
        return f"{self.description} - Qty: {self.qty} @ ${self.price}"

    def clean(self):
        """Validate the invoice line data"""
        super().clean()
        
        # Validate description is not empty
        if not self.description or not self.description.strip():
            raise ValidationError({
                'description': 'Description is required.'
            })
        
        # Validate quantity is positive
        if self.qty <= 0:
            raise ValidationError({
                'qty': 'Quantity must be greater than zero.'
            })
        
        # Validate price is non-negative
        if self.price < 0:
            raise ValidationError({
                'price': 'Price cannot be negative.'
            })

    def save(self, *args, **kwargs):
        # Calculate total before saving
        self.total = self.qty * self.price
        self.full_clean()
        super().save(*args, **kwargs)
        
        # Update invoice totals after saving
        self.invoice.calculate_totals()
        self.invoice.save(update_fields=['subtotal', 'tax_amount', 'total_amount'])


class StatusChange(models.Model):
    """
    StatusChange model for tracking job status changes and creating an audit trail.
    Each status change is recorded with the old status, new status, timestamp, and user.
    """
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='status_changes',
        help_text="Job that had its status changed"
    )
    old_status = models.CharField(
        max_length=20,
        choices=Job.STATUS_CHOICES,
        help_text="Previous status of the job"
    )
    new_status = models.CharField(
        max_length=20,
        choices=Job.STATUS_CHOICES,
        help_text="New status of the job"
    )
    changed_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='status_changes_made',
        help_text="User who made the status change"
    )
    changed_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the status change occurred"
    )
    notes = models.TextField(
        blank=True,
        help_text="Optional notes about the status change"
    )
    
    class Meta:
        verbose_name = "Status Change"
        verbose_name_plural = "Status Changes"
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['job', 'changed_at']),
            models.Index(fields=['changed_by', 'changed_at']),
            models.Index(fields=['new_status', 'changed_at']),
        ]
    
    def __str__(self):
        return f"{self.job.display_name}: {self.old_status} → {self.new_status} ({self.changed_at.strftime('%Y-%m-%d %H:%M')})"
    
    def clean(self):
        """Validate the status change data"""
        super().clean()
        
        # Validate that old and new status are different
        if self.old_status == self.new_status:
            raise ValidationError({
                'new_status': 'New status must be different from old status.'
            })
        
        # Validate status transitions (business rules)
        valid_transitions = {
            'scheduled': ['in_progress', 'canceled'],
            'in_progress': ['completed', 'canceled'],
            'completed': [],  # No further transitions from completed
            'canceled': [],   # No further transitions from canceled
        }
        
        if self.old_status in valid_transitions:
            if self.new_status not in valid_transitions[self.old_status]:
                raise ValidationError({
                    'new_status': f'Cannot transition from {self.get_old_status_display()} to {self.get_new_status_display()}.'
                })
    
    def save(self, *args, **kwargs):
        """Save the status change with validation"""
        self.full_clean()
        super().save(*args, **kwargs)


class PrintTemplateSetting(models.Model):
    """
    PrintTemplateSetting model for configuring branding and layout options for print templates.
    This model stores settings for invoices, work orders, and other printable documents.
    """
    # Template identification
    template_name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique name for the print template (e.g., 'invoice', 'work_order')"
    )
    template_type = models.CharField(
        max_length=50,
        choices=[
            ('invoice', 'Invoice'),
            ('work_order', 'Work Order'),
            ('quote', 'Quote'),
            ('receipt', 'Receipt'),
        ],
        help_text="Type of document this template is for"
    )
    
    # Company branding
    company_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Company name to display on printed documents"
    )
    company_logo_path = models.CharField(
        max_length=500,
        blank=True,
        help_text="Path to company logo file (relative to media directory)"
    )
    company_address = models.TextField(
        blank=True,
        help_text="Company address to display on printed documents"
    )
    company_phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Company phone number to display on printed documents"
    )
    company_email = models.EmailField(
        blank=True,
        help_text="Company email to display on printed documents"
    )
    company_website = models.URLField(
        blank=True,
        help_text="Company website to display on printed documents"
    )
    
    # Document styling
    header_color = models.CharField(
        max_length=7,  # CSS hex color code
        default="#3B82F6",
        help_text="Header background color (CSS hex code)"
    )
    text_color = models.CharField(
        max_length=7,  # CSS hex color code
        default="#000000",
        help_text="Main text color (CSS hex code)"
    )
    accent_color = models.CharField(
        max_length=7,  # CSS hex color code
        default="#1F2937",
        help_text="Accent color for borders and highlights (CSS hex code)"
    )
    font_family = models.CharField(
        max_length=100,
        default="Arial, sans-serif",
        help_text="Font family for printed documents"
    )
    font_size = models.CharField(
        max_length=20,
        default="12px",
        help_text="Base font size for printed documents"
    )
    
    # Layout options
    show_logo = models.BooleanField(
        default=True,
        help_text="Whether to show company logo on printed documents"
    )
    show_company_info = models.BooleanField(
        default=True,
        help_text="Whether to show company information on printed documents"
    )
    show_footer = models.BooleanField(
        default=True,
        help_text="Whether to show footer with additional information"
    )
    footer_text = models.TextField(
        blank=True,
        help_text="Custom footer text for printed documents"
    )
    
    # Document-specific settings
    default_tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=0.0000,
        help_text="Default tax rate for this template (e.g., 0.0825 for 8.25%)"
    )
    currency_symbol = models.CharField(
        max_length=5,
        default="$",
        help_text="Currency symbol to use on printed documents"
    )
    page_size = models.CharField(
        max_length=20,
        choices=[
            ('letter', 'Letter (8.5" x 11")'),
            ('legal', 'Legal (8.5" x 14")'),
            ('a4', 'A4 (210mm x 297mm)'),
        ],
        default='letter',
        help_text="Page size for printed documents"
    )
    orientation = models.CharField(
        max_length=10,
        choices=[
            ('portrait', 'Portrait'),
            ('landscape', 'Landscape'),
        ],
        default='portrait',
        help_text="Page orientation for printed documents"
    )
    
    # System fields
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this template is active and available for use"
    )
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_print_templates',
        help_text="User who created this template"
    )
    updated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_print_templates',
        help_text="User who last updated this template"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Print Template Setting"
        verbose_name_plural = "Print Template Settings"
        ordering = ['template_type', 'template_name']
        indexes = [
            models.Index(fields=['template_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['template_name']),
        ]
    
    def __str__(self):
        return f"{self.get_template_type_display()}: {self.template_name}"
    
    def clean(self):
        """Validate the print template settings"""
        super().clean()
        
        # Validate color format (basic hex validation)
        for color_field in ['header_color', 'text_color', 'accent_color']:
            color_value = getattr(self, color_field)
            if color_value and not color_value.startswith('#'):
                raise ValidationError({
                    color_field: 'Color must be a valid CSS hex color code starting with #'
                })
        
        # Validate tax rate is non-negative
        if self.default_tax_rate < 0:
            raise ValidationError({
                'default_tax_rate': 'Tax rate cannot be negative.'
            })
        
        # Validate template name is not empty
        if not self.template_name or not self.template_name.strip():
            raise ValidationError({
                'template_name': 'Template name is required.'
            })
    
    def save(self, *args, **kwargs):
        """Save the print template settings with validation"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def display_name(self):
        """Get the display name for the template"""
        return f"{self.get_template_type_display()}: {self.template_name}"
    
    @property
    def css_variables(self):
        """Get CSS variables for styling"""
        return {
            '--header-color': self.header_color,
            '--text-color': self.text_color,
            '--accent-color': self.accent_color,
            '--font-family': self.font_family,
            '--font-size': self.font_size,
        }


# Signal handlers for automatic audit trail
@receiver(pre_save, sender=Job)
def create_status_change_record(sender, instance, **kwargs):
    """
    Create a StatusChange record when a job's status changes.
    This provides an automatic audit trail for all status transitions.
    """
    if instance.pk:  # Only for existing instances (not new ones)
        try:
            old_instance = Job.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                # Status has changed, create audit record
                StatusChange.objects.create(
                    job=instance,
                    old_status=old_instance.status,
                    new_status=instance.status,
                    changed_by=getattr(instance, '_current_user', None),  # Set by view
                    notes=getattr(instance, '_status_change_notes', '')  # Set by view
                )
        except Job.DoesNotExist:
            # This shouldn't happen, but handle gracefully
            pass


class AbsoluteFileSystemStorage(FileSystemStorage):
    """Custom storage class that can handle absolute paths and network paths"""
    def __init__(self, location=None, base_url=None):
        super().__init__(location=location or 'licenses/', base_url=base_url)
        self._base_path = None
        self._is_network_path = False
        self._retry_count = 3
        self._retry_delay = 1  # seconds
        logger.info(f"Initializing AbsoluteFileSystemStorage with location: {location}")

    @property
    def base_path(self):
        """Lazy loading of base path from SystemSettings"""
        if self._base_path is None:
            try:
                settings = SystemSettings.objects.first()
                if settings and settings.license_scan_path:
                    self._base_path = os.path.normpath(settings.license_scan_path)
                    self._is_network_path = settings.is_network_path
                    logger.info(f"Loaded base path from settings: {self._base_path} (Network: {self._is_network_path})")
                else:
                    self._base_path = self.location
                    logger.info(f"Using default location as base path: {self._base_path}")
            except Exception as e:
                logger.error(f"Error getting base path: {str(e)}")
                self._base_path = self.location
        return self._base_path

    def _is_network_path(self, path):
        """Check if a path is a network path"""
        return path.startswith('\\\\') or path.startswith('//')

    def _validate_network_path(self, path):
        """Validate network path accessibility using Windows APIs"""
        from rental_scheduler.utils.network import validate_network_path
        is_valid, _, _ = validate_network_path(path)
        return is_valid

    def _retry_operation(self, operation, *args, **kwargs):
        """Retry an operation with exponential backoff"""
        for attempt in range(self._retry_count):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                if attempt == self._retry_count - 1:
                    raise
                logger.warning(f"Operation failed, retrying ({attempt + 1}/{self._retry_count}): {str(e)}")
                time.sleep(self._retry_delay * (2 ** attempt))  # Exponential backoff

    def get_valid_name(self, name):
        """Sanitize the filename to prevent directory traversal"""
        logger.info(f"get_valid_name called with: {name}")
        # If it's an absolute path, return the base filename only
        if os.path.isabs(name):
            return os.path.basename(name)
        # Otherwise use Django's implementation
        return super().get_valid_name(name)

    def path(self, name):
        """Convert the name to a filesystem path"""
        try:
            logger.info(f"path() called with name: {name}")
            if os.path.isabs(name):
                logger.info(f"Path is absolute, returning normalized path: {os.path.normpath(name)}")
                return os.path.normpath(name)
            result = os.path.normpath(os.path.join(self.base_path, name))
            logger.info(f"Path is relative, returning: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in path generation: {str(e)}")
            return super().path(name)

    def url(self, name):
        """Generate a URL for the file"""
        try:
            logger.info(f"url() called with name: {name}")
            if not name:
                return ''
                
            if os.path.isabs(name):
                try:
                    rel_path = os.path.relpath(name, self.base_path)
                    url = f'/licenses/{rel_path.replace(os.sep, "/")}'
                    logger.info(f"Generated URL for absolute path: {url}")
                    return url
                except Exception as e:
                    logger.error(f"Error generating URL for absolute path: {str(e)}")
                    return f'/licenses/{os.path.basename(name)}'
            
            return super().url(name)
        except Exception as e:
            logger.error(f"Error in URL generation: {str(e)}")
            return ''

    def _save(self, name, content):
        """Save the file with proper error handling and retry logic"""
        try:
            logger.info(f"_save() called with name: {name}")
            
            # Handle absolute paths and network paths differently
            if os.path.isabs(name):
                logger.info(f"Handling absolute path save: {name}")
                # Ensure the directory exists
                dir_path = os.path.dirname(name)
                logger.info(f"Creating directory if needed: {dir_path}")
                
                # Use retry logic for directory creation
                self._retry_operation(os.makedirs, dir_path, exist_ok=True)
                
                # Use retry logic for file saving
                def save_file():
                    with open(name, 'wb') as destination:
                        for chunk in content.chunks():
                            destination.write(chunk)
                self._retry_operation(save_file)
                logger.info(f"File saved directly to absolute path: {name}")
                return name
            else:
                # For relative paths, first get the full path
                full_path = self.path(name)
                dir_path = os.path.dirname(full_path)
                logger.info(f"Handling relative path save to: {full_path}")
                
                # Ensure directory exists
                self._retry_operation(os.makedirs, dir_path, exist_ok=True)
                
                # If it's a network path that the storage is configured with
                if self._is_network_path:
                    # Save directly to the network path to bypass Django's security checks
                    def save_file():
                        with open(full_path, 'wb') as destination:
                            for chunk in content.chunks():
                                destination.write(chunk)
                    self._retry_operation(save_file)
                    logger.info(f"File saved to network path: {full_path}")
                    return name
                else:
                    # For standard local paths, use parent class's _save
                    result = super()._save(name, content)
                    logger.info(f"File saved via standard method: {result}")
                    return result
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise

    def delete(self, name):
        """Delete the file with proper error handling and retry logic"""
        try:
            logger.info(f"delete() called with name: {name}")
            full_path = self.path(name)
            
            if os.path.exists(full_path):
                if os.path.isabs(name) or self._is_network_path:
                    # For absolute or network paths, delete directly
                    def remove_file():
                        os.remove(full_path)
                    self._retry_operation(remove_file)
                    logger.info(f"File deleted directly: {full_path}")
                else:
                    # For standard paths, use parent implementation
                    self._retry_operation(super().delete, name)
                    logger.info("File deleted via standard method")
            else:
                logger.warning(f"File not found for deletion: {full_path}")
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            raise

    def get_available_name(self, name, max_length=None):
        """Get a unique name for the file"""
        try:
            logger.info(f"get_available_name() called with name: {name}, max_length: {max_length}")
            # If it's an absolute path, use it as is (we handle uniqueness in get_license_upload_path)
            if os.path.isabs(name):
                logger.info(f"Path is absolute, returning as is: {name}")
                return name
                
            # For relative paths, use parent implementation
            result = super().get_available_name(name, max_length)
            logger.info(f"Path is relative, returning: {result}")
            return result
        except Exception as e:
            logger.error(f"Error getting available name: {str(e)}")
            return name

class SystemSettings(models.Model):
    winch_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Price charged for winch rental"
    )
    hitch_bar_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price charged for hitch bar rental"
    )
    furniture_blanket_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price charged per furniture blanket"
    )
    strap_chain_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price charged per strap or chain"
    )
    evening_pickup_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price charged for evening pickup service"
    )
    tax_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        help_text="Tax rate as a percentage (e.g., 8.25 for 8.25%)"
    )
    license_scan_path = models.CharField(
        max_length=255,
        help_text="Absolute path where license scans will be stored"
    )
    is_network_path = models.BooleanField(
        default=False,
        help_text="Whether the license scan path is a network path"
    )
    last_path_validation = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the license scan path was last validated"
    )
    PATH_VALIDATION_CHOICES = [
        ('valid', 'Valid'),
        ('invalid', 'Invalid'),
        ('checking', 'Checking'),
        ('error', 'Error'),
    ]
    path_validation_status = models.CharField(
        max_length=20,
        choices=PATH_VALIDATION_CHOICES,
        default='checking',
        help_text="Current validation status of the license scan path"
    )
    path_validation_error = models.TextField(
        null=True,
        blank=True,
        help_text="Error message if path validation failed"
    )

    class Meta:
        verbose_name_plural = "System Settings"
    
    def clean(self):
        from rental_scheduler.utils.network import validate_network_path
        super().clean()
        if self.license_scan_path:
            try:
                # Normalize the path
                self.license_scan_path = os.path.normpath(self.license_scan_path)
                
                # Check if it's a network path
                self.is_network_path = self.license_scan_path.startswith('\\\\') or self.license_scan_path.startswith('//')
                
                # Update validation status
                self.path_validation_status = 'checking'
                self.path_validation_error = None
                
                # Use our new validation function
                is_valid, is_network, error_message = validate_network_path(self.license_scan_path)
                
                if is_valid:
                    self.path_validation_status = 'valid'
                    self.last_path_validation = timezone.now()
                    logger.info(f"Path validation successful: {self.license_scan_path}")
                else:
                    if self.is_network_path:
                        # For network paths, don't raise validation error
                        self.path_validation_status = 'invalid'
                        self.path_validation_error = error_message
                        logger.warning(f"Network path validation failed: {error_message}")
                    else:
                        # For local paths, enforce validation
                        self.path_validation_status = 'error'
                        self.path_validation_error = error_message
                        logger.error(f"Local path validation failed: {error_message}")
                        raise ValidationError({'license_scan_path': error_message})
                        
            except Exception as e:
                self.path_validation_status = 'error'
                self.path_validation_error = f'Invalid path: {str(e)}'
                logger.error(f"Path validation error: {str(e)}")
                raise ValidationError({'license_scan_path': f'Invalid path: {str(e)}'})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        # Ensure only one instance exists
        if not self.pk and SystemSettings.objects.exists():
            raise ValidationError('Only one SystemSettings instance can exist.')
        super().save(*args, **kwargs)

    def validate_path(self):
        """Validate the license scan path and update status"""
        try:
            self.clean()  # This will update validation status
            return True
        except ValidationError:
            return False

    def get_path_status_display(self):
        """Get a human-readable status of the path"""
        if self.path_validation_status == 'valid':
            return f"Valid (Last checked: {self.last_path_validation.strftime('%Y-%m-%d %H:%M:%S')})"
        elif self.path_validation_status == 'error':
            return f"Error: {self.path_validation_error}"
        else:
            return self.get_path_validation_status_display()

class TrailerCategory(models.Model):
    category = models.CharField(
        max_length=100,
        help_text="Category name for grouping trailers"
    )
    
    class Meta:
        verbose_name_plural = "Trailer Categories"
    
    def __str__(self):
        return self.category

class Trailer(models.Model):
    """
    Trailer model for the repair & rental shop scheduling system.
    Represents physical trailer assets that can be rented or repaired.
    """
    # Basic Information
    category = models.ForeignKey(TrailerCategory, on_delete=models.PROTECT)
    number = models.CharField(
        max_length=50, 
        unique=True,
        help_text="Unique identifier for the trailer"
    )
    model = models.CharField(
        max_length=100,
        help_text="Trailer model name or description"
    )
    
    # Customer Relationship (for owned trailers)
    customer = models.ForeignKey(
        'Customer', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Customer who owns this trailer (if applicable)"
    )
    
    # Identification Information
    serial_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Manufacturer serial number"
    )
    color = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Trailer color for identification"
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Freeform description of trailer features or condition"
    )
    
    # Physical Specifications
    hauling_capacity = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Maximum weight capacity in pounds"
    )
    width = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        help_text="Width in feet"
    )
    length = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        help_text="Length in feet"
    )
    height = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        help_text="Height in feet"
    )
    
    # Rental Rates (for rental trailers)
    half_day_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Rate charged for half-day rental"
    )
    daily_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Rate charged for full-day rental"
    )
    weekly_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Rate charged for weekly rental"
    )
    
    # Status and Availability
    is_available = models.BooleanField(
        default=True,
        help_text="Whether this trailer is available for rental"
    )
    is_rental_trailer = models.BooleanField(
        default=True,
        help_text="Whether this trailer is available for rental (vs customer-owned)"
    )
    
    # Additional Information
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about the trailer"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['number']),
            models.Index(fields=['serial_number']),
            models.Index(fields=['color']),
            models.Index(fields=['customer']),
            models.Index(fields=['is_available']),
            models.Index(fields=['is_rental_trailer']),
            # Composite indexes for common search patterns
            models.Index(fields=['category', 'is_available']),
            models.Index(fields=['customer', 'is_rental_trailer']),
        ]
        ordering = ['number']

    def __str__(self):
        """Return a human-readable representation of the trailer"""
        if self.customer and not self.is_rental_trailer:
            return f"{self.number} - {self.model} (Owned by {self.customer.display_name})"
        else:
            return f"{self.number} - {self.model}"
    
    @property
    def display_name(self):
        """Get the primary display name for the trailer"""
        return f"{self.number} - {self.model}"
    
    @property
    def search_text(self):
        """Get searchable text for the trailer"""
        search_parts = []
        if self.number:
            search_parts.append(self.number)
        if self.model:
            search_parts.append(self.model)
        if self.serial_number:
            search_parts.append(self.serial_number)
        if self.color:
            search_parts.append(self.color)
        if self.description:
            search_parts.append(self.description)
        if self.customer:
            search_parts.append(self.customer.display_name)
        return ' '.join(search_parts)
    
    @property
    def dimensions(self):
        """Get formatted dimensions string"""
        dims = []
        if self.length:
            dims.append(f"{self.length}'L")
        if self.width:
            dims.append(f"{self.width}'W")
        if self.height:
            dims.append(f"{self.height}'H")
        return ' x '.join(dims) if dims else None
    
    @property
    def is_rentable(self):
        """Check if trailer is available for rental"""
        return self.is_rental_trailer and self.is_available and not self.is_under_service
    
    def clean(self):
        """Validate the trailer data"""
        super().clean()
        
        # Ensure trailer number is unique
        if self.number:
            existing = Trailer.objects.filter(number__iexact=self.number)
            if self.pk:
                existing = existing.exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError({
                    'number': 'A trailer with this number already exists.'
                })
        
        # Validate serial number uniqueness if provided
        if self.serial_number:
            existing = Trailer.objects.filter(serial_number__iexact=self.serial_number)
            if self.pk:
                existing = existing.exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError({
                    'serial_number': 'A trailer with this serial number already exists.'
                })
        
        # Validate dimensions are positive if provided
        for field_name in ['length', 'width', 'height']:
            value = getattr(self, field_name)
            if value is not None and value <= 0:
                raise ValidationError({
                    field_name: f'{field_name.title()} must be greater than zero.'
                })
        
        # Validate hauling capacity is positive
        if self.hauling_capacity <= 0:
            raise ValidationError({
                'hauling_capacity': 'Hauling capacity must be greater than zero.'
            })
    
    def save(self, *args, **kwargs):
        """Save the trailer with validation"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def is_under_service(self):
        """
        Check if the trailer is currently under service.
        
        Args:
            at: datetime to check. If None, uses current time.
            
        Returns:
            bool: True if trailer is under service at the given time
        """
        at = timezone.now()
        return self.trailerservice_set.filter(
            start_datetime__lte=at,
            end_datetime__gt=at
        ).exists()
    
    @property
    def active_services(self):
        """
        Get all currently active services for this trailer.
        
        Returns:
            QuerySet: Active TrailerService instances
        """
        at = timezone.now()
        return self.trailerservice_set.filter(
            start_datetime__lte=at,
            end_datetime__gt=at
        )
    
    @property
    def upcoming_services(self):
        """
        Get all upcoming/future services for this trailer.
        
        Returns:
            QuerySet: Future TrailerService instances
        """
        at = timezone.now()
        return self.trailerservice_set.filter(
            start_datetime__gt=at
        ).order_by('start_datetime')
    
    @property
    def has_scheduled_services(self):
        """
        Check if trailer has any scheduled services (active or upcoming).
        
        Returns:
            bool: True if trailer has active or upcoming services
        """
        at = timezone.now()
        return self.trailerservice_set.filter(
            end_datetime__gt=at
        ).exists()
    
    @property
    def completed_services(self):
        """
        Get all completed/old services for this trailer.
        
        Returns:
            QuerySet: Completed TrailerService instances
        """
        at = timezone.now()
        return self.trailerservice_set.filter(
            end_datetime__lte=at
        ).order_by('-end_datetime')
    
    @classmethod
    def get_sorted_by_size(cls, queryset=None):
        """
        Return trailers sorted by size (length first, then width).
        Shorter lengths come first, then shorter widths within the same length.
        
        Args:
            queryset: Optional queryset to sort. If None, uses all trailers.
            
        Returns:
            list: Sorted list of trailer objects
        """
        if queryset is None:
            trailers = list(cls.objects.all())
        else:
            trailers = list(queryset)
        
        # Sort by length first, then by width
        # Items with unparseable dimensions (0,0) will sort to the beginning
        trailers.sort(key=lambda t: (float(t.length or 0), float(t.width or 0)))
        
        return trailers

def get_license_upload_path(instance, filename):
    """
    Dynamically determine the upload path based on SystemSettings.
    Falls back to 'licenses/' if no settings exist.
    """
    try:
        logger.info(f"get_license_upload_path called with filename: {filename}")
        settings = SystemSettings.objects.first()
        if not settings or not settings.license_scan_path:
            logger.warning("No valid license scan path configured in settings")
            raise ValueError("No valid license scan path configured in settings")

        # Normalize the base path
        base_path = os.path.normpath(settings.license_scan_path)
        logger.info(f"Base path from settings: {base_path}")
        
        if not os.path.exists(base_path):
            logger.warning(f"License scan path does not exist: {base_path}")
            raise ValueError(f"License scan path does not exist: {base_path}")
        
        # Create the directory structure with normalized paths
        date_path = datetime.now().strftime('%Y/%m')
        full_path = os.path.normpath(os.path.join(base_path, date_path))
        logger.info(f"Full path for file: {full_path}")
        
        os.makedirs(full_path, exist_ok=True)
        
        # Validate file extension
        file_ext = os.path.splitext(filename)[1].lower()
        allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
        if file_ext not in allowed_extensions:
            logger.warning(f"Invalid file extension: {file_ext}")
            raise ValueError(f"Invalid file extension. Allowed: {', '.join(allowed_extensions)}")
        
        # Generate a unique filename - sanitize and allow only safe characters
        sanitized_name = instance.name.replace(' ', '_').lower()
        # Further sanitize to remove any potentially problematic characters
        sanitized_name = ''.join(c for c in sanitized_name if c.isalnum() or c == '_')
        unique_id = uuid.uuid4().hex[:8]
        file_name = f"{sanitized_name}_{unique_id}{file_ext}"
        final_path = os.path.normpath(os.path.join(full_path, file_name))
        
        # Ensure the final path is within the base directory
        if not os.path.abspath(final_path).startswith(os.path.abspath(base_path)):
            logger.warning(f"Generated path is outside base directory: {final_path}")
            raise ValueError("Generated path is outside base directory")
        
        logger.info(f"Final upload path: {final_path}")
        return final_path
        
    except Exception as e:
        logger.error(f"Error in get_license_upload_path: {str(e)}")
        # Fall back to default location in media root
        date_path = datetime.now().strftime('%Y/%m')
        fallback_path = os.path.normpath(os.path.join('licenses', date_path, filename))
        logger.info(f"Using fallback path: {fallback_path}")
        return fallback_path

class Customer(models.Model):
    # Business Information
    business_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Business or company name"
    )
    contact_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Primary contact person's name"
    )
    
    # Contact Information
    phone = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message='Enter a valid phone number. Format: +1234567890'
            )
        ],
        help_text="Primary contact phone number",
        blank=True,
        null=True
    )
    alt_phone = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message='Enter a valid phone number. Format: +1234567890'
            )
        ],
        help_text="Alternative phone number",
        blank=True,
        null=True
    )
    email = models.EmailField(
        blank=True,
        null=True,
        help_text="Contact email address"
    )
    
    # Address Information
    address_line1 = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Street address line 1"
    )
    address_line2 = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Street address line 2 (apartment, suite, etc.)"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="City name"
    )
    state = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        help_text="Two-letter state code"
    )
    postal_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="ZIP or postal code"
    )
    
    # Additional Information
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about the customer"
    )
    po_number = models.CharField(
        max_length=50, 
        blank=True,
        null=True,
        help_text="Purchase order number (optional)"
    )
    drivers_license_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Customer's driver's license number"
    )
    drivers_license_scan = models.FileField(
        upload_to=get_license_upload_path,
        storage=AbsoluteFileSystemStorage(),
        null=True,
        blank=True,
        help_text="Scanned copy of driver's license"
    )
    drivers_license_scanned = models.BooleanField(
        default=False,
        help_text="Indicates if a physical license has been scanned"
    )
    
    # Legacy field for backward compatibility
    name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Legacy field - use business_name or contact_name instead"
    )
    street_address = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Legacy field - use address_line1 instead"
    )
    zip_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="Legacy field - use postal_code instead"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['business_name']),
            models.Index(fields=['contact_name']),
            models.Index(fields=['phone']),
            models.Index(fields=['email']),
            models.Index(fields=['city']),
            models.Index(fields=['state']),
            # Composite indexes for common search patterns
            models.Index(fields=['business_name', 'contact_name']),
            models.Index(fields=['phone', 'alt_phone']),
            models.Index(fields=['city', 'state']),
        ]
        ordering = ['business_name', 'contact_name']

    def __str__(self):
        """Return a human-readable representation of the customer"""
        if self.business_name and self.contact_name:
            return f"{self.business_name} - {self.contact_name}"
        elif self.business_name:
            return self.business_name
        elif self.contact_name:
            return self.contact_name
        elif self.name:  # Legacy fallback
            return self.name
        else:
            return f"Customer #{self.id}"
    
    @property
    def display_name(self):
        """Get the primary display name for the customer"""
        if self.business_name:
            return self.business_name
        elif self.contact_name:
            return self.contact_name
        elif self.name:  # Legacy fallback
            return self.name
        else:
            return f"Customer #{self.id}"
    
    @property
    def primary_phone(self):
        """Get the primary phone number"""
        return self.phone or self.alt_phone
    
    @property
    def full_address(self):
        """Get the complete address as a formatted string"""
        address_parts = []
        if self.address_line1:
            address_parts.append(self.address_line1)
        if self.address_line2:
            address_parts.append(self.address_line2)
        if self.city:
            address_parts.append(self.city)
        if self.state:
            address_parts.append(self.state)
        if self.postal_code:
            address_parts.append(self.postal_code)
        return ', '.join(address_parts) if address_parts else None
    
    def clean(self):
        """Validate the customer data"""
        super().clean()
        
        # Ensure at least one name field is provided
        if not any([self.business_name, self.contact_name, self.name]):
            raise ValidationError({
                'business_name': 'At least one name field (Business Name, Contact Name, or Name) must be provided.'
            })
        
        # Ensure at least one phone number is provided
        if not any([self.phone, self.alt_phone]):
            raise ValidationError({
                'phone': 'At least one phone number must be provided.'
            })
    
    def save(self, *args, **kwargs):
        logger.info("Starting Customer.save()")
        
        # Update drivers_license_scanned based on file presence
        self.drivers_license_scanned = bool(self.drivers_license_scan)
        if self.drivers_license_scan:
            logger.info(f"License scan file present: {self.drivers_license_scan.name}")
        
        # Validate before saving
        self.full_clean()
        
        try:
            super().save(*args, **kwargs)
            logger.info("Successfully saved customer")
        except Exception as e:
            logger.error(f"Error saving customer: {str(e)}")
            raise

class Contract(models.Model):
    # Relationships
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    trailer = models.ForeignKey(Trailer, on_delete=models.PROTECT)
    
    # Rental Details
    start_datetime = models.DateTimeField(
        help_text="When the rental period begins"
    )
    end_datetime = models.DateTimeField(
        help_text="When the rental period ends"
    )
    category = models.ForeignKey(TrailerCategory, on_delete=models.PROTECT)
    
    # Add-on Features
    includes_winch = models.BooleanField(
        default=False,
        help_text="Whether this rental includes a winch"
    )
    includes_hitch_bar = models.BooleanField(
        default=False,
        help_text="Whether this rental includes a hitch bar"
    )
    furniture_blanket_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of furniture blankets included"
    )
    strap_chain_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of straps or chains included"
    )
    has_evening_pickup = models.BooleanField(
        default=False,
        help_text="Whether this rental includes evening pickup service"
    )
    
    stored_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="The rate that was calculated and stored when the contract was created"
    )
    rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Calculated rate based on duration"
    )
    custom_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Override the standard rate calculation with a custom amount"
    )
    extra_mileage = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Additional charges for extra mileage"
    )
    
    # Financial Information
    subtotal = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Subtotal before tax"
    )
    tax_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Tax amount calculated"
    )
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Total amount including tax"
    )
    down_payment = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Initial payment amount"
    )
    balance_due = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Remaining balance to be paid"
    )
    
    # Status Flags
    PAYMENT_TYPE_CHOICES = [
        ('cash', 'Cash Payment'),
        ('charge', 'Charge Payment'),
    ]
    
    PAYMENT_TIMING_CHOICES = [
        ('pickup', 'Payment at Pickup'),
        ('return', 'Payment at Return'),
    ]
    
    show_in_calendar = models.BooleanField(
        default=True,
        help_text="Whether to display this contract in the calendar view"
    )
    is_picked_up = models.BooleanField(
        default=False,
        help_text="Whether the trailer has been picked up"
    )
    pickup_datetime = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When the trailer was actually picked up"
    )
    is_returned = models.BooleanField(
        default=False,
        help_text="Whether the trailer has been returned"
    )
    return_datetime = models.DateTimeField(
        null=True, 
        blank=True
    )
    payment_type = models.CharField(
        max_length=10, 
        choices=PAYMENT_TYPE_CHOICES,
        help_text="Type of payment accepted"
    )
    payment_timing = models.CharField(
        max_length=10, 
        choices=PAYMENT_TIMING_CHOICES,
        default='pickup',
        help_text="When payment is due"
    )
    is_billed = models.BooleanField(
        default=False,
        help_text="Whether an invoice has been generated"
    )
    is_invoiced = models.BooleanField(
        default=False,
        help_text="Whether payment has been received"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['start_datetime']),
            models.Index(fields=['end_datetime']),
            models.Index(fields=['is_picked_up']),
            models.Index(fields=['is_returned']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_datetime__gt=models.F('start_datetime')),
                name='end_after_start'
            )
        ]

    def __str__(self):
        return f"Contract #{self.id} - {self.customer.name} - {self.trailer.number}"

    def calculate_duration(self):
        """Calculate the rental duration in days using centralized service"""
        from rental_scheduler.services.rental_calculator import RentalCalculator
        
        duration_info = RentalCalculator.calculate_duration_info(
            self.start_datetime, 
            self.end_datetime
        )
        return duration_info['days']

    def calculate_rate(self):
        """
        Calculate the appropriate rate based on duration using centralized service.
        Maintains priority order: stored_rate > custom_rate > calculated_rate.
        """
        # Priority order: stored_rate > custom_rate > calculated_rate
        if self.stored_rate:
            return self.stored_rate
            
        if self.custom_rate:
            return self.custom_rate
        
        # Use centralized service for calculation
        from rental_scheduler.services.rental_calculator import RentalCalculator
        
        duration = self.calculate_duration()
        return RentalCalculator.calculate_base_rate(
            trailer=self.trailer,
            duration_days=duration,
            custom_rate=None  # We handle custom_rate above
        )

    def _calculate_fresh_rate(self):
        """
        Calculate a fresh rate ignoring stored_rate, used during save() for recalculation.
        """
        if self.custom_rate:
            return self.custom_rate
        
        # Use centralized service for calculation
        from rental_scheduler.services.rental_calculator import RentalCalculator
        
        duration = self.calculate_duration()
        return RentalCalculator.calculate_base_rate(
            trailer=self.trailer,
            duration_days=duration,
            custom_rate=None
        )

    def calculate_add_ons(self):
        """Calculate the total cost of all add-ons using centralized service"""
        from rental_scheduler.services.rental_calculator import RentalCalculator
        
        settings = SystemSettings.objects.first()
        addon_costs = RentalCalculator.calculate_addon_costs(
            settings=settings,
            includes_winch=self.includes_winch,
            includes_hitch_bar=self.includes_hitch_bar,
            furniture_blanket_count=self.furniture_blanket_count,
            strap_chain_count=self.strap_chain_count,
            has_evening_pickup=self.has_evening_pickup
        )
        return addon_costs['total_addon_cost']

    def calculate_subtotal(self):
        """Calculate subtotal including all add-ons and extra mileage"""
        from rental_scheduler.services.rental_calculator import RentalCalculator
        
        # Use centralized service for consistent calculation
        settings = SystemSettings.objects.first()
        base_rate = self.calculate_rate()
        addon_costs = self.calculate_add_ons()
        
        totals = RentalCalculator.calculate_totals(
            base_rate=Decimal(str(base_rate)),
            addon_costs=Decimal(str(addon_costs)),
            extra_mileage=Decimal(str(self.extra_mileage)),
            tax_rate=Decimal(str(settings.tax_rate if settings else 0)),
            down_payment=Decimal(str(self.down_payment))
        )
        return totals['subtotal']

    def calculate_tax(self):
        """Calculate tax amount based on subtotal using centralized service"""
        from rental_scheduler.services.rental_calculator import RentalCalculator
        
        # Use centralized service for consistent calculation
        settings = SystemSettings.objects.first()
        base_rate = self.calculate_rate()
        addon_costs = self.calculate_add_ons()
        
        totals = RentalCalculator.calculate_totals(
            base_rate=Decimal(str(base_rate)),
            addon_costs=Decimal(str(addon_costs)),
            extra_mileage=Decimal(str(self.extra_mileage)),
            tax_rate=Decimal(str(settings.tax_rate if settings else 0)),
            down_payment=Decimal(str(self.down_payment))
        )
        return totals['tax_amount']

    def calculate_total(self):
        """Calculate total amount including tax using centralized service"""
        from rental_scheduler.services.rental_calculator import RentalCalculator
        
        # Use centralized service for consistent calculation
        settings = SystemSettings.objects.first()
        base_rate = self.calculate_rate()
        addon_costs = self.calculate_add_ons()
        
        totals = RentalCalculator.calculate_totals(
            base_rate=Decimal(str(base_rate)),
            addon_costs=Decimal(str(addon_costs)),
            extra_mileage=Decimal(str(self.extra_mileage)),
            tax_rate=Decimal(str(settings.tax_rate if settings else 0)),
            down_payment=Decimal(str(self.down_payment))
        )
        return totals['total_amount']

    def calculate_balance(self):
        """Calculate remaining balance using centralized service"""
        from rental_scheduler.services.rental_calculator import RentalCalculator
        
        # Use centralized service for consistent calculation
        settings = SystemSettings.objects.first()
        base_rate = self.calculate_rate()
        addon_costs = self.calculate_add_ons()
        
        totals = RentalCalculator.calculate_totals(
            base_rate=Decimal(str(base_rate)),
            addon_costs=Decimal(str(addon_costs)),
            extra_mileage=Decimal(str(self.extra_mileage)),
            tax_rate=Decimal(str(settings.tax_rate if settings else 0)),
            down_payment=Decimal(str(self.down_payment))
        )
        return totals['balance_due']

    def save(self, *args, **kwargs):
        # Define price-sensitive fields that should trigger recalculation
        price_sensitive_fields = {
            'start_datetime', 'end_datetime', 'trailer_id', 'custom_rate',
            'includes_winch', 'includes_hitch_bar', 'furniture_blanket_count',
            'strap_chain_count', 'has_evening_pickup', 'extra_mileage', 'down_payment'
        }
        
        # Check if we need to recalculate pricing due to field changes
        recalc_needed = False
        if self.pk:
            try:
                original = Contract.objects.get(pk=self.pk)
                # Check if any price-sensitive fields have changed
                for field_name in price_sensitive_fields:
                    if getattr(original, field_name) != getattr(self, field_name):
                        recalc_needed = True
                        logger.info(f"Contract {self.pk}: Price recalculation needed due to {field_name} change")
                        break
                        
                # Invalidate cached PDF if relevant fields changed
                exclude_fields = {'updated_at'}
                for field in self._meta.fields:
                    name = field.name
                    if name in exclude_fields:
                        continue
                    if getattr(original, name) != getattr(self, name):
                        break
            except Contract.DoesNotExist:
                # New contract, recalculation will happen anyway
                pass

        # Updated pricing logic with change detection
        # Priority: custom_rate > stored_rate (if no changes) > calculated_rate
        if self.custom_rate:
            # Custom rate always takes precedence
            self.stored_rate = self.custom_rate
            self.rate = self.custom_rate
        elif not self.stored_rate or recalc_needed:
            # Calculate rate if no stored rate exists or price-sensitive fields changed
            calculated_rate = self._calculate_fresh_rate()
            self.stored_rate = calculated_rate
            self.rate = calculated_rate
        else:
            # stored_rate already set and no relevant changes – ensure rate mirrors it
            self.rate = self.stored_rate

        # Always recompute derived financial fields to guarantee consistency
        self.subtotal = self.calculate_subtotal()
        self.tax_amount = self.calculate_tax()
        self.total_amount = self.calculate_total()
        self.balance_due = self.calculate_balance()

        super().save(*args, **kwargs)

    def clean(self):
        """Validate the contract data"""
        super().clean()
        
        # Validate return datetime is set when trailer is returned
        if self.is_returned and not self.return_datetime:
            raise ValidationError({
                'return_datetime': 'Return date/time is required when trailer is marked as returned.'
            })
            
        # Validate return datetime is after start datetime
        if self.return_datetime and self.return_datetime < self.start_datetime:
            raise ValidationError({
                'return_datetime': 'Return date/time must be after start date/time.'
            })

    # Add these properties to get individual fees
    @property
    def winch_fee(self):
        """Calculate the winch fee"""
        settings = SystemSettings.objects.first()
        if settings and self.includes_winch:
            return settings.winch_price
        return Decimal('0')

    @property
    def hitch_bar_fee(self):
        """Calculate the hitch bar fee"""
        settings = SystemSettings.objects.first()
        if settings and self.includes_hitch_bar:
            return settings.hitch_bar_price
        return Decimal('0')

    @property
    def furniture_blanket_fee(self):
        """Calculate the furniture blanket fee"""
        settings = SystemSettings.objects.first()
        if settings and self.furniture_blanket_count > 0:
            return settings.furniture_blanket_price * self.furniture_blanket_count
        return Decimal('0')
        
    @property
    def strap_chain_fee(self):
        """Calculate the strap/chain fee"""
        settings = SystemSettings.objects.first()
        if settings and self.strap_chain_count > 0:
            return settings.strap_chain_price * self.strap_chain_count
        return Decimal('0')
        
    @property
    def evening_pickup_fee(self):
        """Calculate the evening pickup fee"""
        settings = SystemSettings.objects.first()
        if settings and self.has_evening_pickup:
            return settings.evening_pickup_price
        return Decimal('0')

class TrailerService(models.Model):
    """
    Represents a service/maintenance period when a trailer is temporarily unavailable
    """
    trailer = models.ForeignKey(
        Trailer, 
        on_delete=models.CASCADE,
        help_text="Trailer being serviced"
    )
    start_datetime = models.DateTimeField(
        help_text="When the service period begins",
        db_index=True
    )
    end_datetime = models.DateTimeField(
        help_text="When the service period ends",
        db_index=True
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        help_text="Description of the service being performed"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['start_datetime']),
            models.Index(fields=['end_datetime']),
            models.Index(fields=['trailer', 'start_datetime']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_datetime__gt=models.F('start_datetime')),
                name='service_end_after_start'
            )
        ]
        verbose_name = "Trailer Service"
        verbose_name_plural = "Trailer Services"

    def __str__(self):
        return f"Service: {self.trailer.number} ({format_local(self.start_datetime)} - {format_local(self.end_datetime)})"

    def clean(self):
        """Validate the service data"""
        super().clean()
        
        # Validate end datetime is after start datetime
        if self.end_datetime and self.start_datetime and self.end_datetime <= self.start_datetime:
            raise ValidationError({
                'end_datetime': 'End date/time must be after start date/time.'
            })
            
        # Check for overlapping service periods for the same trailer
        if self.trailer_id:
            overlapping_services = TrailerService.objects.filter(
                trailer=self.trailer,
                start_datetime__lt=self.end_datetime,
                end_datetime__gt=self.start_datetime
            )
            
            # Exclude current instance if updating
            if self.pk:
                overlapping_services = overlapping_services.exclude(pk=self.pk)
                
            if overlapping_services.exists():
                # Create a detailed, user-friendly error message
                conflict_service = overlapping_services.first()
                conflict_start = format_local(conflict_service.start_datetime)
                conflict_end = format_local(conflict_service.end_datetime)
                conflict_desc = conflict_service.description or "Maintenance"
                
                error_message = (
                    f"This time conflicts with an existing service:\n\n"
                    f"• {conflict_desc}\n"
                    f"• From {conflict_start} to {conflict_end}\n\n"
                    f"Please choose a different time period that doesn't overlap."
                )
                
                # Use non-field error for better display
                raise ValidationError(error_message)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        """Check if this service period is currently active"""
        now = timezone.now()
        return self.start_datetime <= now < self.end_datetime

    @property
    def is_future(self):
        """Check if this service period is in the future"""
        return self.start_datetime > timezone.now()
 
    @property
    def is_past(self):
        """Check if this service period is in the past"""
        return self.end_datetime <= timezone.now()


