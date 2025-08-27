import os
import logging
import platform
import re
from pathlib import Path
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
import traceback

logger = logging.getLogger(__name__)

# Conditionally import Windows-specific modules
if platform.system() == 'Windows':
    try:
        import win32net
        import win32api
        import win32wnet
        WINDOWS_SUPPORT = True
        logger.info("Windows network support enabled with pywin32")
    except ImportError as e:
        logger.warning(f"pywin32 not available - Windows network paths may not work correctly: {str(e)}")
        WINDOWS_SUPPORT = False
else:
    WINDOWS_SUPPORT = False
    logger.info(f"Not running on Windows ({platform.system()}), network path support limited")

def sanitize_network_path(path):
    """
    Sanitize a network path to prevent path traversal.
    
    Args:
        path: Path to sanitize
        
    Returns:
        str: Sanitized path
    """
    if not path:
        return path
    
    # Normalize slashes for the platform
    path = path.replace('/', '\\') if platform.system() == 'Windows' else path.replace('\\', '/')
    
    # Remove any ../ or ./ components
    path = os.path.normpath(path)
    
    # Check if it's a UNC path and ensure it's properly formatted
    if path.startswith('\\\\') or path.startswith('//'):
        # Ensure no invalid characters
        # Only allow alphanumeric, spaces, dashes, underscores and \/:. in the path
        if re.search(r'[^\w\s\-\\/:.]', path):
            logger.warning(f"Path contains invalid characters: {path}")
            # Remove invalid characters
            path = re.sub(r'[^\w\s\-\\/:.]', '', path)
            
    return path

def connect_to_network_share(unc_path, username=None, password=None):
    """
    Connect to a Windows network share.
    
    Args:
        unc_path: UNC path (\\server\share)
        username: Optional username for authentication
        password: Optional password for authentication
        
    Returns:
        bool: True if connected successfully, False otherwise
    """
    # Sanitize and validate the UNC path
    unc_path = sanitize_network_path(unc_path)
    
    if not (unc_path.startswith('\\\\') or unc_path.startswith('//')):
        logger.error(f"Invalid UNC path format: {unc_path}")
        return False
        
    # Normalize path format for Windows
    unc_path = unc_path.replace('/', '\\')
    
    # For non-Windows systems, we'll still try basic access
    if not WINDOWS_SUPPORT:
        logger.info(f"Non-Windows system, trying standard access to: {unc_path}")
        return os.path.exists(unc_path)
    
    try:
        # If credentials are provided, use them
        if username and password:
            logger.info(f"Connecting to {unc_path} with credentials")
            # Create a NETRESOURCE structure
            nr = win32wnet.NETRESOURCE()
            nr.lpRemoteName = unc_path
            nr.dwType = 0  # RESOURCETYPE_ANY
            
            # Connect to the network resource
            win32wnet.WNetAddConnection2(nr, password, username, 0)
        else:
            # Try to connect with current Windows credentials
            logger.info(f"Connecting to {unc_path} with current Windows credentials")
            # For simple connections with current credentials, we can use a simpler approach
            try:
                # Check if already connected, if not, connect using current credentials
                win32wnet.WNetAddConnection2(win32wnet.NETRESOURCE(), "", "", 0)
            except Exception:
                # If already connected or other issue, just continue
                pass
                
        # Verify we can access the path
        exists = os.path.exists(unc_path)
        logger.info(f"Network path {unc_path} exists: {exists}")
        return exists
        
    except Exception as e:
        logger.error(f"Failed to connect to network share: {str(e)}")
        return False

def validate_network_path(path):
    """
    Validate if a network path is accessible.
    
    Args:
        path (str): The network path to validate
        
    Returns:
        tuple: (is_valid, is_network_path, error_message)
    """
    if not path:
        return False, False, "Path cannot be empty"
    
    # Sanitize the path
    path = sanitize_network_path(path)
    
    # Normalize path
    path = os.path.normpath(path)
    
    # Check if it's a network path
    is_network_path = path.startswith('\\\\') or path.startswith('//')
    
    if not is_network_path:
        # For local paths, just check existence
        exists = os.path.exists(path)
        error = None if exists else "Local path does not exist"
        return exists, False, error
    
    # Handle network path
    if connect_to_network_share(path):
        # Try to write a test file
        try:
            test_file = os.path.join(path, '.test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            return True, True, None
        except Exception as e:
            error_msg = f"Path exists but is not writable: {str(e)}"
            logger.warning(error_msg)
            return False, True, error_msg
    else:
        return False, True, "Network path is not accessible"

def disconnect_network_share(unc_path):
    """
    Disconnect from a Windows network share.
    
    Args:
        unc_path: UNC path to disconnect from
        
    Returns:
        bool: True if disconnected, False otherwise
    """
    if not WINDOWS_SUPPORT:
        return True
        
    try:
        # Normalize path format for Windows
        unc_path = unc_path.replace('/', '\\')
        
        # Try to disconnect
        win32wnet.WNetCancelConnection2(unc_path, 0, 0)
        logger.info(f"Disconnected from network share: {unc_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to disconnect from network share: {str(e)}")
        return False

def is_django_path_allowed(path):
    """
    Check if a path would be allowed by Django's path security.
    
    Args:
        path: Path to check
        
    Returns:
        bool: True if the path would be allowed, False otherwise
    """
    try:
        # Check for path traversal attempts (.. sequences)
        normalized = os.path.normpath(path)
        if '..' in normalized.split(os.sep):
            return False
            
        # Check for absolute paths on non-Windows
        if not platform.system() == 'Windows' and os.path.isabs(path):
            return False
        
        # Check Windows UNC paths
        if path.startswith('\\\\') or path.startswith('//'):
            # In Django these would be caught by path traversal checks
            return False
            
        return True
    except Exception as e:
        logger.error(f"Error checking path security: {str(e)}")
        return False

def get_last_n_lines(file_path, n=500):
    """
    Get the last n lines from a file efficiently.
    
    Args:
        file_path (str): Path to the log file
        n (int): Number of lines to retrieve (default: 500)
        
    Returns:
        str: Last n lines of the file
    """
    try:
        if not os.path.exists(file_path):
            return f"Log file not found: {file_path}"
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            lines = file.readlines()
            last_lines = lines[-n:] if len(lines) > n else lines
            return ''.join(last_lines)
    except Exception as e:
        return f"Error reading log file {file_path}: {str(e)}"

def get_system_logs(lines=500):
    """
    Retrieve the last n lines from all system log files.
    
    Args:
        lines (int): Number of lines to retrieve from each log file
        
    Returns:
        dict: Dictionary containing log contents from different log files
    """
    logs = {}
    
    # Get log directory from settings
    log_dir = getattr(settings, 'LOGS_DIR', settings.BASE_DIR / 'logs')
    
    # Define log files to read
    log_files = {
        'main_log': log_dir / 'gts_scheduler.log',
        'error_log': log_dir / 'error.log',
    }
    
    for log_name, log_path in log_files.items():
        logs[log_name] = get_last_n_lines(str(log_path), lines)
    
    return logs

def send_error_email(error_details, request=None, exception=None):
    """
    Send an error report email with system logs.
    
    Args:
        error_details (dict): Dictionary containing error information
        request: Django request object (optional)
        exception: Exception object (optional)
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Get system logs
        logs = get_system_logs(500)
        
        # Prepare email context
        context = {
            'error_details': error_details,
            'logs': logs,
            'timestamp': timezone.now(),
            'request_info': {
                'path': request.path if request else 'N/A',
                'method': request.method if request else 'N/A',
                'user': str(request.user) if request and hasattr(request, 'user') else 'N/A',
                'ip': request.META.get('REMOTE_ADDR', 'N/A') if request else 'N/A',
                'user_agent': request.META.get('HTTP_USER_AGENT', 'N/A') if request else 'N/A',
            },
            'exception_info': {
                'type': type(exception).__name__ if exception else 'N/A',
                'message': str(exception) if exception else 'N/A',
                'traceback': traceback.format_exc() if exception else 'N/A',
            }
        }
        
        # Create email subject
        error_code = error_details.get('error_code', 'Unknown')
        subject = f'GTS Scheduler Error Report - {error_code}'
        
        # Create email body
        message = f"""
GTS Scheduler Error Report
=========================

Error Details:
- Error Code: {error_details.get('error_code', 'N/A')}
- Error ID: {error_details.get('error_id', 'N/A')}
- Timestamp: {context['timestamp']}
- Request Path: {context['request_info']['path']}
- User: {context['request_info']['user']}
- IP Address: {context['request_info']['ip']}

Exception Information:
- Type: {context['exception_info']['type']}
- Message: {context['exception_info']['message']}

System Logs (Last 500 lines):
==============================

Main Log:
{logs.get('main_log', 'No main log available')}

Error Log:
{logs.get('error_log', 'No error log available')}

Traceback:
{context['exception_info']['traceback']}
"""
        
        # Send email
        recipient_email = getattr(settings, 'ERROR_REPORT_EMAIL', 'sales@rocksoliddata.solutions')
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@rocksoliddata.solutions')
        
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        
        logger.info(f"Error report email sent successfully to {recipient_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send error report email: {str(e)}")
        return False 