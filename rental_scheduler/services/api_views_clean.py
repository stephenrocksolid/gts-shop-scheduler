"""
API views for rental calculation services.
Simplified version without trailer/contract dependencies.
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

# Simplified system - no longer using Trailer or SystemSettings models

@require_http_methods(["GET"])
def get_calculation_constants(request):
    """
    Get calculation constants for JavaScript frontend.
    Simplified version with basic constants.
    """
    try:
        constants = {
            'tax_rate': 0.0825,  # Default 8.25% tax rate
            'winch_price': 25.00,
            'hitch_bar_price': 15.00,
            'furniture_blanket_price': 5.00,
            'strap_chain_price': 3.00,
            'evening_pickup_price': 50.00,
        }
        
        return JsonResponse({
            'success': True,
            'constants': constants
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error getting calculation constants: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def calculate_duration_info(request):
    """
    Calculate duration information between two dates.
    """
    try:
        import json
        from datetime import datetime
        
        data = json.loads(request.body)
        
        start_str = data.get('start_datetime')
        end_str = data.get('end_datetime')
        
        if not start_str or not end_str:
            return JsonResponse({
                'success': False,
                'error': 'Both start_datetime and end_datetime are required'
            }, status=400)
        
        # Parse datetime strings
        start_dt = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
        
        if end_dt <= start_dt:
            return JsonResponse({
                'success': False,
                'error': 'End datetime must be after start datetime'
            }, status=400)
        
        # Calculate duration
        duration = end_dt - start_dt
        total_hours = duration.total_seconds() / 3600
        total_days = total_hours / 24
        
        return JsonResponse({
            'success': True,
            'duration_info': {
                'total_hours': round(total_hours, 2),
                'total_days': round(total_days, 2),
                'duration_display': f"{int(total_days)} days, {int(total_hours % 24)} hours"
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error calculating duration: {str(e)}'
        }, status=500)


# Placeholder functions for deleted functionality
def calculate_rental_quote(request):
    """Disabled - depends on deleted trailer models"""
    return JsonResponse({
        'success': False,
        'error': 'Rental quote calculation is not available in simplified system'
    }, status=501)
