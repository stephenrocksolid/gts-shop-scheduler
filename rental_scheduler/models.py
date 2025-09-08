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
    Job model for managing repair work orders and scheduled jobs.
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
    
    def save(self, *args, **kwargs):
        """Save the status change with validation"""
        self.full_clean()
        super().save(*args, **kwargs)


# Placeholder functions for migration compatibility
def get_license_upload_path(instance, filename):
    """Placeholder function for migration compatibility"""
    return f'licenses/{filename}'

class AbsoluteFileSystemStorage:
    """Placeholder class for migration compatibility"""
    pass

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
