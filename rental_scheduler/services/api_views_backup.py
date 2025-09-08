"""
API views for real-time rental calculations.
These endpoints provide JSON responses for JavaScript frontend.
"""
import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

# Simplified system - no longer using Trailer or SystemSettings models
from rental_scheduler.services.rental_calculator import RentalCalculator


# Disabled - depends on deleted models
# @require_http_methods(["POST"])
# @csrf_exempt
# def calculate_rental_quote(request):
    """
    Calculate a complete rental quote for JavaScript frontend.
    
    Expected POST data (JSON):
    {
        "trailer_id": int,
        "start_datetime": "YYYY-MM-DD HH:MM:SS",
        "end_datetime": "YYYY-MM-DD HH:MM:SS",
        "custom_rate": float (optional),
        "extra_mileage": float (optional),
        "down_payment": float (optional),
        "includes_winch": bool (optional),
        "includes_hitch_bar": bool (optional),
        "furniture_blanket_count": int (optional),
        "strap_chain_count": int (optional),
        "has_evening_pickup": bool (optional)
    }
    
    Returns JSON with complete quote information.
    """
    try:
        # Parse JSON data
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['trailer_id', 'start_datetime', 'end_datetime']
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }, status=400)
        
        # Get trailer
        try:
            trailer = Trailer.objects.get(id=data['trailer_id'])
        except ObjectDoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Trailer not found'
            }, status=404)
        
        # Parse datetimes
        try:
            start_datetime = datetime.strptime(data['start_datetime'], '%Y-%m-%d %H:%M:%S')
            end_datetime = datetime.strptime(data['end_datetime'], '%Y-%m-%d %H:%M:%S')
            
            # Make timezone-aware
            if timezone.is_naive(start_datetime):
                start_datetime = timezone.make_aware(start_datetime)
            if timezone.is_naive(end_datetime):
                end_datetime = timezone.make_aware(end_datetime)
                
        except ValueError as e:
            return JsonResponse({
                'success': False,
                'error': f'Invalid datetime format: {str(e)}'
            }, status=400)
        
        # Get system settings
        settings = SystemSettings.objects.first()
        
        # Parse optional fields with defaults
        custom_rate = None
        if 'custom_rate' in data and data['custom_rate']:
            try:
                custom_rate = Decimal(str(data['custom_rate']))
            except (InvalidOperation, ValueError):
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid custom_rate format'
                }, status=400)
        
        try:
            extra_mileage = Decimal(str(data.get('extra_mileage', 0)))
            down_payment = Decimal(str(data.get('down_payment', 0)))
        except (InvalidOperation, ValueError):
            return JsonResponse({
                'success': False,
                'error': 'Invalid number format for extra_mileage or down_payment'
            }, status=400)
        
        # Addon options
        addon_kwargs = {
            'includes_winch': data.get('includes_winch', False),
            'includes_hitch_bar': data.get('includes_hitch_bar', False),
            'furniture_blanket_count': int(data.get('furniture_blanket_count', 0)),
            'strap_chain_count': int(data.get('strap_chain_count', 0)),
            'has_evening_pickup': data.get('has_evening_pickup', False)
        }
        
        # Calculate complete quote using our service
        quote = RentalCalculator.calculate_complete_quote(
            trailer=trailer,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            settings=settings,
            custom_rate=custom_rate,
            extra_mileage=extra_mileage,
            down_payment=down_payment,
            **addon_kwargs
        )
        
        # Convert Decimal values to float for JSON serialization
        def decimal_to_float(obj):
            if isinstance(obj, Decimal):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: decimal_to_float(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [decimal_to_float(item) for item in obj]
            return obj
        
        quote_json = decimal_to_float(quote)
        
        # Add trailer information
        quote_json['trailer_info'] = {
            'id': trailer.id,
            'number': trailer.number,
            'model': trailer.model,
            'size': f"{float(trailer.length):g}'x{float(trailer.width):g}'" if trailer.width and trailer.length else '',
            'width': float(trailer.width) if trailer.width else None,
            'length': float(trailer.length) if trailer.length else None,
            'half_day_rate': float(trailer.half_day_rate),
            'daily_rate': float(trailer.daily_rate),
            'weekly_rate': float(trailer.weekly_rate)
        }
        
        return JsonResponse({
            'success': True,
            'quote': quote_json
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def get_calculation_constants(request):
    """
    Return calculation constants for JavaScript validation.
    
    Returns JSON with business rule constants.
    """
    try:
        constants = RentalCalculator.get_calculation_constants()
        
        # Add pricing rules for display
        constants['pricing_rules'] = RentalCalculator.get_pricing_rules_display()
        
        # Add system settings if available
        settings = SystemSettings.objects.first()
        if settings:
            constants['system_settings'] = {
                'tax_rate': float(settings.tax_rate),
                'winch_price': float(settings.winch_price),
                'hitch_bar_price': float(settings.hitch_bar_price),
                'furniture_blanket_price': float(settings.furniture_blanket_price),
                'strap_chain_price': float(settings.strap_chain_price),
                'evening_pickup_price': float(settings.evening_pickup_price)
            }
        
        return JsonResponse({
            'success': True,
            'constants': constants
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def calculate_duration_info(request):
    """
    Calculate duration information for given start/end datetimes.
    
    Expected POST data (JSON):
    {
        "start_datetime": "YYYY-MM-DD HH:MM:SS",
        "end_datetime": "YYYY-MM-DD HH:MM:SS"
    }
    
    Returns JSON with duration information.
    """
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        if 'start_datetime' not in data or 'end_datetime' not in data:
            return JsonResponse({
                'success': False,
                'error': 'Missing required fields: start_datetime, end_datetime'
            }, status=400)
        
        # Parse datetimes
        try:
            start_datetime = datetime.strptime(data['start_datetime'], '%Y-%m-%d %H:%M:%S')
            end_datetime = datetime.strptime(data['end_datetime'], '%Y-%m-%d %H:%M:%S')
            
            # Make timezone-aware
            if timezone.is_naive(start_datetime):
                start_datetime = timezone.make_aware(start_datetime)
            if timezone.is_naive(end_datetime):
                end_datetime = timezone.make_aware(end_datetime)
                
        except ValueError as e:
            return JsonResponse({
                'success': False,
                'error': f'Invalid datetime format: {str(e)}'
            }, status=400)
        
        # Calculate duration info
        duration_info = RentalCalculator.calculate_duration_info(start_datetime, end_datetime)
        
        return JsonResponse({
            'success': True,
            'duration_info': duration_info
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=500) 