from django.shortcuts import render
from django.utils import timezone
from django.conf import settings
import uuid
import logging
from rental_scheduler.utils.network import get_system_logs
import urllib.parse
import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from rental_scheduler.utils.network import send_error_email

logger = logging.getLogger(__name__)

def get_error_context(request, error_code, error_message=None, exception=None):
    """
    Generate common context for error pages
    """
    error_id = str(uuid.uuid4())
    timestamp = timezone.now()
    
    context = {
        'error_code': error_code,
        'timestamp': timestamp,
        'request_path': request.path,
        'referrer': request.META.get('HTTP_REFERER'),
        'error_id': error_id,
        'debug': settings.DEBUG,
    }
    
    if error_message and settings.DEBUG:
        context['error_message'] = error_message
    
    # For server errors, include system logs for mailto functionality
    if error_code >= 500:
        system_logs = get_system_logs(50)
        context['system_logs'] = system_logs
        email_body = f"""GTS Scheduler Error Report

Error Details:
Error Code: {error_code}
Error ID: {error_id}
Timestamp: {timestamp}
Request Path: {request.path}
User: {request.user.username if request.user.is_authenticated else 'Anonymous'}

System Logs (Last 50 lines):

Main Log:
{system_logs.get('main_log', 'No main log available')}

Error Log:
{system_logs.get('error_log', 'No error log available')}

Please describe what you were doing when this error occurred:
[Please add your description here]
"""
        subject = urllib.parse.quote(f"GTS Scheduler Error Report - {error_code}")
        body = urllib.parse.quote(email_body)
        context['mailto_link'] = f"mailto:sales@rocksoliddata.solutions?subject={subject}&body={body}"
        
    # Log the error
    log_message = f"""
    Error {error_code}
    ID: {error_id}
    Time: {timestamp}
    Path: {request.path}
    User: {request.user if request.user.is_authenticated else 'Anonymous'}
    """
    if error_message:
        log_message += f"\nError Message: {error_message}"
        
    if error_code >= 500:
        logger.error(log_message)
    else:
        logger.warning(log_message)
        
    return context

def handler404(request, exception):
    """
    Handle 404 Not Found errors
    """
    context = get_error_context(request, 404)
    return render(request, 'error/404.html', context, status=404)

def handler500(request):
    """
    Handle 500 Server errors
    """
    context = get_error_context(request, 500)
    return render(request, 'error/500.html', context, status=500)

def handler403(request, exception):
    """
    Handle 403 Forbidden errors
    """
    context = get_error_context(request, 403, str(exception), exception)
    return render(request, 'error/403.html', context, status=403)

def handler400(request, exception):
    """
    Handle 400 Bad Request errors
    """
    context = get_error_context(request, 400, str(exception), exception)
    return render(request, 'error/400.html', context, status=400) 

@csrf_exempt
@require_POST
def send_error_report(request):
    """Send error report email via POST."""
    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid method')
    try:
        data = json.loads(request.body.decode())
    except Exception:
        return HttpResponseBadRequest('Invalid JSON')
    error_code = data.get('error_code')
    error_id = data.get('error_id')
    if not error_code or not error_id:
        return HttpResponseBadRequest('Missing fields')
    error_details = {'error_code': error_code, 'error_id': error_id}
    sent = send_error_email(error_details, request)
    return JsonResponse({'sent': sent}) 