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

# Create your models here.

logger = logging.getLogger(__name__)

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
    hauling_capacity = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Maximum weight capacity in pounds"
    )
    half_day_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Rate charged for half-day rental"
    )
    daily_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Rate charged for full-day rental"
    )
    weekly_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Rate charged for weekly rental"
    )
    width = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Width in feet")
    length = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Length in feet")
    is_available = models.BooleanField(
        default=True,
        help_text="Whether this trailer is available for rental"
    )

    def __str__(self):
        return f"{self.number} - {self.model}"
    
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
    name = models.CharField(
        max_length=200,
        help_text="Full name of the customer"
    )
    phone = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message='Enter a valid phone number. Format: +1234567890'
            )
        ],
        help_text="Contact phone number",
        blank=True,
        null=True
    )
    street_address = models.CharField(
        max_length=200,
        help_text="Street address",
        blank=True,
        null=True
    )
    city = models.CharField(
        max_length=100,
        help_text="City name",
        blank=True,
        null=True
    )
    state = models.CharField(
        max_length=2,
        help_text="Two-letter state code",
        blank=True,
        null=True
    )
    zip_code = models.CharField(
        max_length=10,
        help_text="ZIP or postal code",
        blank=True,
        null=True
    )
    po_number = models.CharField(
        max_length=50, 
        blank=True,
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.phone})"
    
    def save(self, *args, **kwargs):
        logger.info("Starting Customer.save()")
        # Update drivers_license_scanned based on file presence
        self.drivers_license_scanned = bool(self.drivers_license_scan)
        if self.drivers_license_scan:
            logger.info(f"License scan file present: {self.drivers_license_scan.name}")
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


