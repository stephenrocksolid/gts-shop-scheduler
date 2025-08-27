from django import template
from decimal import Decimal
from rental_scheduler.services.rental_calculator import RentalCalculator

register = template.Library()

@register.simple_tag
def format_rate_label(rate_category, has_half_day=False, half_day_rate=None):
    """
    Format rate label with category information.
    Single source of truth for rate label formatting across templates and JavaScript.
    
    Args:
        rate_category: The rate category ('half_day', 'daily', 'weekly', 'extended')
        has_half_day: Whether there's a half-day component (for daily + half day)
        half_day_rate: Optional half-day rate to display for daily + half day
        
    Returns:
        Formatted rate label string
        
    Usage: 
        {% format_rate_label rate_category has_half_day %}
        {% format_rate_label rate_category has_half_day half_day_rate %}
    """
    if not rate_category:
        return 'Rate'
    
    # Handle daily with half-day component
    if rate_category.lower() == 'daily' and has_half_day:
        label = 'Rate (Daily + half day'
        if half_day_rate is not None:
            label += f': ${half_day_rate:.2f}'
        label += ')'
        return label
    
    # Handle all other categories
    display_category = rate_category.replace('_', ' ').title()
    return f'Rate ({display_category})'

@register.filter(name='format_duration_category')
def format_duration_category(contract):
    """
    Format duration category for a contract using RentalCalculator service
    Usage: {{ contract|format_duration_category }}
    """
    if not contract or not contract.start_datetime or not contract.end_datetime:
        return 'Invalid dates'
    
    try:
        calculator = RentalCalculator()
        duration_info = calculator.calculate_duration_info(
            contract.start_datetime, 
            contract.end_datetime
        )
        return duration_info['category']
    except Exception:
        return 'Error calculating duration'

@register.filter(name='format_duration_display')
def format_duration_display(contract):
    """
    Format duration display for a contract using centralized RentalCalculator logic
    Usage: {{ contract|format_duration_display }}
    
    Note: This is a legacy template tag. Use 'display_duration' for new development.
    Both now use the same centralized logic for consistency.
    """
    if not contract or not contract.start_datetime or not contract.end_datetime:
        return 'Invalid dates'
    
    try:
        duration_info = RentalCalculator.calculate_duration_info(
            contract.start_datetime, 
            contract.end_datetime
        )
        
        # Use centralized formatting method - single source of truth
        return RentalCalculator.format_duration_display(duration_info)
        
    except Exception:
        return 'Error calculating duration'

@register.filter(name='get_rate_type')
def get_rate_type(contract):
    """
    Get the rate type for a contract using RentalCalculator service
    Usage: {{ contract|get_rate_type }}
    """
    if not contract or not contract.trailer:
        return 'Unknown'
    
    # If custom rate is set, indicate that
    if contract.custom_rate and contract.custom_rate > 0:
        return 'Custom Rate'
    
    # If stored rate exists, use that
    if contract.stored_rate and contract.stored_rate > 0:
        return 'Stored Rate'
    
    try:
        calculator = RentalCalculator()
        if contract.start_datetime and contract.end_datetime:
            duration_info = calculator.calculate_duration_info(
                contract.start_datetime, 
                contract.end_datetime
            )
            return f"{duration_info['category']} Rate"
        else:
            return 'Calculated Rate'
    except Exception:
        return 'Standard Rate'

@register.simple_tag
def calculate_rate_for_display(contract):
    """
    Calculate and return rate information for display
    Usage: {% calculate_rate_for_display contract as rate_info %}
    """
    if not contract or not contract.trailer:
        return {
            'amount': Decimal('0.00'),
            'type': 'Unknown',
            'category': 'Unknown'
        }
    
    try:
        # Use the contract's existing rate calculation which now uses the service
        rate = contract.calculate_rate()
        rate_type = get_rate_type(contract)
        
        if contract.start_datetime and contract.end_datetime:
            calculator = RentalCalculator()
            duration_info = calculator.calculate_duration_info(
                contract.start_datetime, 
                contract.end_datetime
            )
            category = duration_info['category']
        else:
            category = 'Unknown'
        
        return {
            'amount': rate,
            'type': rate_type,
            'category': category
        }
    except Exception:
        return {
            'amount': Decimal('0.00'),
            'type': 'Error',
            'category': 'Error'
        }

@register.filter(name='safe_currency')
def safe_currency(value):
    """
    Safely format currency values with error handling
    Usage: {{ contract.rate|safe_currency }}
    """
    try:
        if value is None:
            return '$0.00'
        
        # Convert to Decimal for precise calculation
        if isinstance(value, str):
            value = Decimal(value)
        elif not isinstance(value, Decimal):
            value = Decimal(str(value))
        
        return f"${value:.2f}"
    except (ValueError, TypeError, AttributeError):
        return '$0.00'

@register.filter(name='display_duration')
def display_duration(contract):
    """
    Format duration using centralized RentalCalculator logic
    Usage: {{ contract|display_duration }}
    """
    if not contract or not contract.start_datetime or not contract.end_datetime:
        return 'Invalid duration'
    
    try:
        duration_info = RentalCalculator.calculate_duration_info(
            contract.start_datetime, 
            contract.end_datetime
        )
        
        # Use centralized formatting method - single source of truth
        return RentalCalculator.format_duration_display(duration_info)
        
    except Exception:
        return 'Error calculating duration'

@register.filter(name='unit_rate')
def unit_rate(contract):
    """
    Calculate unit rate matching the frontend logic
    Usage: {{ contract|unit_rate }}
    """
    if not contract or not contract.trailer:
        return Decimal('0.00')
    
    try:
        # Check for custom rate first
        if contract.custom_rate and contract.custom_rate > 0:
            return contract.custom_rate
        
        # Calculate duration info
        duration_info = RentalCalculator.calculate_duration_info(
            contract.start_datetime, 
            contract.end_datetime
        )
        
        rate_category = duration_info.get('rate_category')
        
        if rate_category == 'half_day':
            return contract.trailer.half_day_rate
        elif rate_category == 'daily':
            return contract.trailer.daily_rate
        elif rate_category == 'weekly':
            return contract.trailer.weekly_rate
        elif rate_category == 'extended':
            return contract.trailer.weekly_rate / Decimal('6')
        
        # Fallback to daily rate
        return contract.trailer.daily_rate
        
    except Exception:
        return Decimal('0.00')

@register.filter(name='safe_duration_fallback')
def safe_duration_fallback(contract):
    """
    Safe duration display with fallback for PDF generation
    Usage: {{ contract|safe_duration_fallback }}
    """
    try:
        # Use the new display_duration filter
        return display_duration(contract)
    except Exception:
        # Fallback to simple calculation for PDF reliability
        try:
            if not contract or not contract.start_datetime or not contract.end_datetime:
                return 'Invalid dates'
            
            duration = contract.calculate_duration()
            if duration <= 0.21:  # Approximately 5 hours
                return 'Half Day'
            elif duration <= 7:
                days = int(duration)
                return f"{days} Day{'s' if days != 1 else ''}"
            else:
                days = int(duration)
                return f"{days} Days"
        except Exception:
            return 'Duration unknown' 