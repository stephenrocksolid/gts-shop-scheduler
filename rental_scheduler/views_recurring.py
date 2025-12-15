"""
Updated views for recurring events support.
These will replace/augment the existing job create/update/delete endpoints.
"""

import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, date

from rental_scheduler.models import Job, Calendar
from rental_scheduler.utils.events import normalize_event_datetimes


# Date validation constants (match Job model)
MIN_VALID_YEAR = 2000
MAX_VALID_YEAR = 2100
MAX_JOB_SPAN_DAYS = 365


def validate_job_dates(start_dt, end_dt):
    """
    Validate job dates for API endpoints.
    Returns (is_valid, error_message) tuple.
    """
    if not start_dt or not end_dt:
        return True, None
    
    # Check year ranges
    if start_dt.year < MIN_VALID_YEAR or start_dt.year > MAX_VALID_YEAR:
        return False, f'Start year must be between {MIN_VALID_YEAR} and {MAX_VALID_YEAR}. Got: {start_dt.year}'
    
    if end_dt.year < MIN_VALID_YEAR or end_dt.year > MAX_VALID_YEAR:
        return False, f'End year must be between {MIN_VALID_YEAR} and {MAX_VALID_YEAR}. Got: {end_dt.year}'
    
    # Check span
    span_days = (end_dt - start_dt).days
    if span_days > MAX_JOB_SPAN_DAYS:
        return False, f'Job cannot span more than {MAX_JOB_SPAN_DAYS} days. Current span: {span_days} days.'
    
    return True, None


@require_http_methods(["POST"])
@csrf_protect
def job_create_api_recurring(request):
    """
    API endpoint to create a new job with recurring support.
    
    Accepts additional 'recurrence' parameter:
    {
        "business_name": "ABC Company",
        "start": "2025-01-01T09:00:00",
        "end": "2025-01-01T17:00:00",
        "recurrence": {
            "enabled": true,
            "type": "monthly",
            "interval": 2,
            "count": 12,
            "until_date": "2025-12-31"
        }
    }
    """
    try:
        # Parse JSON data
        data = json.loads(request.body)
        print(f"DEBUG: Received data: {data}")
        
        # Create new job
        job = Job()
        
        # Set job fields
        job.business_name = data.get('business_name', '')
        job.contact_name = data.get('contact_name', '')
        job.phone = data.get('phone', '')
        job.address_line1 = data.get('address_line1', '')
        job.address_line2 = data.get('address_line2', '')
        job.city = data.get('city', '')
        job.state = data.get('state', '')
        job.postal_code = data.get('postal_code', '')
        job.trailer_color = data.get('trailer_color', '')
        job.trailer_serial = data.get('trailer_serial', '')
        job.trailer_details = data.get('trailer_details', '')
        job.notes = data.get('notes', '')
        job.repair_notes = data.get('repair_notes', '')
        job.status = data.get('status', 'uncompleted')
        
        # Handle quote (can be text or number)
        if data.get('quote'):
            job.quote = str(data.get('quote'))
        
        # Handle legacy repeat settings (keep for backward compatibility)
        job.repeat_type = data.get('repeat_type', 'none') or 'none'
        if job.repeat_type == 'monthly':
            job.repeat_n_months = int(data.get('repeat_n_months', data.get('repeat_months', 1)))
        else:
            job.repeat_n_months = None
        
        # Determine if this is an all-day event
        all_day = data.get('allDay', data.get('all_day', False))
        if isinstance(all_day, str):
            all_day = all_day.lower() in ('true', '1', 'yes', 'on')
        job.all_day = bool(all_day)
        
        # Handle call reminder
        has_call_reminder = data.get('has_call_reminder', False)
        if isinstance(has_call_reminder, str):
            has_call_reminder = has_call_reminder.lower() in ('true', '1', 'yes', 'on')
        job.has_call_reminder = bool(has_call_reminder)
        
        call_reminder_completed = data.get('call_reminder_completed', False)
        if isinstance(call_reminder_completed, str):
            call_reminder_completed = call_reminder_completed.lower() in ('true', '1', 'yes', 'on')
        job.call_reminder_completed = bool(call_reminder_completed)
        
        if job.has_call_reminder and data.get('call_reminder_weeks_prior'):
            try:
                weeks = int(data.get('call_reminder_weeks_prior'))
                if weeks in [2, 3]:
                    job.call_reminder_weeks_prior = weeks
            except (ValueError, TypeError):
                pass
        
        # Handle dates with normalization for all-day events
        start_value = data.get('start', data.get('start_dt'))
        end_value = data.get('end', data.get('end_dt'))
        
        if start_value:
            try:
                start_dt_utc, end_dt_utc, _, _, _ = normalize_event_datetimes(
                    start_value,
                    end_value,
                    job.all_day
                )
                job.start_dt = start_dt_utc
                job.end_dt = end_dt_utc
                
                # Early validation to give better error messages
                is_valid, error_msg = validate_job_dates(start_dt_utc, end_dt_utc)
                if not is_valid:
                    return JsonResponse({'error': error_msg}, status=400)
                    
            except (ValueError, TypeError) as e:
                return JsonResponse({'error': f'Invalid date format: {str(e)}'}, status=400)
        
        # Set calendar
        calendar_id = data.get('calendar_id', data.get('calendar'))
        if calendar_id:
            try:
                job.calendar = Calendar.objects.get(pk=calendar_id, is_active=True)
            except Calendar.DoesNotExist:
                # Fall back to first active calendar
                job.calendar = Calendar.objects.filter(is_active=True).first()
        else:
            job.calendar = Calendar.objects.filter(is_active=True).first()
        
        if not job.calendar:
            return JsonResponse({'error': 'No active calendar found'}, status=400)
        
        # Set created_by if user is authenticated
        if request.user.is_authenticated:
            job.created_by = request.user
        
        # Save the parent job first
        print(f"DEBUG: Saving parent job with start_dt={job.start_dt}, end_dt={job.end_dt}")
        job.save()
        print(f"DEBUG: Parent job saved with ID: {job.id}")
        
        # Handle recurring event creation
        recurrence = data.get('recurrence', {})
        if recurrence and recurrence.get('enabled'):
            # Don't allow instances to become recurring parents
            if job.recurrence_parent:
                return JsonResponse({
                    'error': 'Cannot make a recurring instance into a new recurring series. Edit the parent series instead.'
                }, status=400)
            
            try:
                # Parse recurrence parameters
                recur_type = recurrence.get('type', 'monthly')
                interval = int(recurrence.get('interval', 1))
                count = recurrence.get('count')
                until_date_str = recurrence.get('until_date')
                
                # Validate count if provided
                if count:
                    count_int = int(count)
                    if count_int > 500:
                        return JsonResponse({'error': 'Recurrence count cannot exceed 500 occurrences.'}, status=400)
                
                # Parse until_date if provided
                until_date = None
                if until_date_str:
                    try:
                        until_date = timezone.make_aware(datetime.fromisoformat(until_date_str))
                    except (ValueError, TypeError):
                        pass
                
                # Create recurrence rule
                job.create_recurrence_rule(
                    recurrence_type=recur_type,
                    interval=interval,
                    count=int(count) if count else None,
                    until_date=until_date
                )
                
                # Generate recurring instances
                instances = job.generate_recurring_instances(
                    count=int(count) if count else None,
                    until_date=until_date
                )
                
                print(f"DEBUG: Generated {len(instances)} recurring instances")
                
            except Exception as e:
                print(f"DEBUG: Error creating recurrence: {e}")
                # Continue without failing - parent job is already saved
        
        # Return created job data with proper formatting
        response_data = _format_job_response(job)
        response_data['recurrence_created'] = bool(recurrence and recurrence.get('enabled'))
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"DEBUG: Error creating job: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_protect
def job_update_api_recurring(request, pk):
    """
    API endpoint for updating job data with recurring support.
    
    Supports 'update_scope' parameter:
    - "this_only": Update only this job
    - "this_and_future": Update this job and all future instances
    - "all": Update all jobs in the series (parent and all instances)
    
    Example:
    {
        "business_name": "Updated Name",
        "update_scope": "this_and_future"
    }
    """
    try:
        job = get_object_or_404(Job, pk=pk)
        data = json.loads(request.body)
        
        # Determine update scope
        update_scope = data.get('update_scope', 'this_only')
        
        # Get the fields that can be updated
        updatable_fields = {}
        field_mapping = {
            'business_name': 'business_name',
            'contact_name': 'contact_name',
            'phone': 'phone',
            'address_line1': 'address_line1',
            'address_line2': 'address_line2',
            'city': 'city',
            'state': 'state',
            'postal_code': 'postal_code',
            'trailer_color': 'trailer_color',
            'trailer_serial': 'trailer_serial',
            'trailer_details': 'trailer_details',
            'notes': 'notes',
            'repair_notes': 'repair_notes',
            'status': 'status',
            'has_call_reminder': 'has_call_reminder',
            'call_reminder_weeks_prior': 'call_reminder_weeks_prior',
            'call_reminder_completed': 'call_reminder_completed',
        }
        
        # Build update dictionary
        for api_field, model_field in field_mapping.items():
            if api_field in data:
                updatable_fields[model_field] = data[api_field]
                setattr(job, model_field, data[api_field])
        
        # Handle repeat settings
        if 'repeat_type' in data:
            job.repeat_type = data.get('repeat_type', 'none') or 'none'
            if job.repeat_type == 'monthly':
                job.repeat_n_months = int(data.get('repeat_n_months', data.get('repeat_months', 1)))
            else:
                job.repeat_n_months = None
        
        # Handle all_day
        if 'allDay' in data or 'all_day' in data:
            all_day = data.get('allDay', data.get('all_day', job.all_day))
            if isinstance(all_day, str):
                all_day = all_day.lower() in ('true', '1', 'yes', 'on')
            job.all_day = bool(all_day)
        
        # Handle call reminder
        if 'has_call_reminder' in data:
            has_call_reminder = data.get('has_call_reminder', False)
            if isinstance(has_call_reminder, str):
                has_call_reminder = has_call_reminder.lower() in ('true', '1', 'yes', 'on')
            job.has_call_reminder = bool(has_call_reminder)
            
            if job.has_call_reminder and 'call_reminder_weeks_prior' in data:
                try:
                    weeks = int(data.get('call_reminder_weeks_prior'))
                    if weeks in [2, 3]:
                        job.call_reminder_weeks_prior = weeks
                except (ValueError, TypeError):
                    pass
            elif not job.has_call_reminder:
                job.call_reminder_weeks_prior = None
        
        # Handle call reminder completed checkbox
        if 'call_reminder_completed' in data:
            call_reminder_completed = data.get('call_reminder_completed', False)
            if isinstance(call_reminder_completed, str):
                call_reminder_completed = call_reminder_completed.lower() in ('true', '1', 'yes', 'on')
            job.call_reminder_completed = bool(call_reminder_completed)
        
        # Handle dates
        start_value = data.get('start', data.get('start_dt'))
        end_value = data.get('end', data.get('end_dt'))
        
        if start_value or end_value:
            if not start_value:
                start_value = job.start_dt
            if not end_value:
                end_value = job.end_dt
            
            try:
                start_dt_utc, end_dt_utc, _, _, _ = normalize_event_datetimes(
                    start_value,
                    end_value,
                    job.all_day
                )
                
                # Early validation to give better error messages
                is_valid, error_msg = validate_job_dates(start_dt_utc, end_dt_utc)
                if not is_valid:
                    return JsonResponse({'error': error_msg}, status=400)
                
                job.start_dt = start_dt_utc
                job.end_dt = end_dt_utc
            except (ValueError, TypeError) as e:
                return JsonResponse({'error': f'Invalid date format: {str(e)}'}, status=400)
        
        # Set updated_by
        if request.user.is_authenticated:
            job.updated_by = request.user
        
        # Save this job with update_fields to avoid validating unchanged fields
        # Build the list of fields to save
        fields_to_save = list(updatable_fields.keys()) if updatable_fields else []
        
        # Add updated_by if authenticated
        if request.user.is_authenticated and 'updated_by' not in fields_to_save:
            fields_to_save.append('updated_by')
        
        # Only use update_fields if we're actually updating specific fields
        if fields_to_save:
            job.save(update_fields=fields_to_save)
        else:
            job.save()
        
        # Handle recurring updates based on scope
        instances_updated = 0
        if update_scope == 'this_and_future' and job.is_recurring_instance:
            # Update this and all future instances
            parent = job.recurrence_parent
            if parent and updatable_fields:
                instances_updated = parent.update_recurring_instances(
                    update_type='future',
                    after_date=job.recurrence_original_start,
                    fields_to_update=updatable_fields
                )
        elif update_scope == 'all':
            # Update all instances in the series
            parent = job.recurrence_parent if job.is_recurring_instance else job
            if parent and updatable_fields:
                # Update parent first
                for field, value in updatable_fields.items():
                    if field != 'status':  # Don't change parent status
                        setattr(parent, field, value)
                parent.save()
                
                # Update all instances
                instances_updated = parent.update_recurring_instances(
                    update_type='all',
                    fields_to_update=updatable_fields
                )
        
        # Return response
        response_data = _format_job_response(job)
        response_data['instances_updated'] = instances_updated
        response_data['update_scope'] = update_scope
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"DEBUG: Error updating job: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_protect
def job_cancel_future_api(request, pk):
    """
    Cancel all future recurrences of a job from a specified date.
    
    POST /api/jobs/<pk>/cancel-future/
    {
        "from_date": "2025-06-01"
    }
    """
    try:
        job = get_object_or_404(Job, pk=pk)
        data = json.loads(request.body)
        
        # Get the from_date
        from_date_str = data.get('from_date')
        if not from_date_str:
            return JsonResponse({'error': 'from_date is required'}, status=400)
        
        try:
            from_date = date.fromisoformat(from_date_str)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
        
        # Determine which job is the parent
        parent = job if job.is_recurring_parent else job.recurrence_parent
        
        if not parent:
            return JsonResponse({'error': 'This job is not part of a recurring series'}, status=400)
        
        # Cancel future recurrences
        canceled_count, parent_updated = parent.cancel_future_recurrences(from_date)
        
        return JsonResponse({
            'success': True,
            'canceled_count': canceled_count,
            'end_recurrence_date': parent.end_recurrence_date.isoformat() if parent.end_recurrence_date else None,
            'parent_id': parent.id,
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"DEBUG: Error canceling future recurrences: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST", "DELETE"])
@csrf_protect
def job_delete_api_recurring(request, pk):
    """
    Delete a job with scope support for recurring events.
    
    POST /api/jobs/<pk>/delete-recurring/
    Body: {"delete_scope": "this_only" | "this_and_future" | "all"}
    
    Scopes:
    - this_only: Delete only this job (default)
    - all: Delete entire series (parent + all instances)
    - this_and_future: Delete this and all future instances
    """
    try:
        job = get_object_or_404(Job, pk=pk)
        
        # Get scope from POST body
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                scope = data.get('delete_scope', 'this_only')
            except json.JSONDecodeError:
                scope = 'this_only'
        else:
            scope = request.GET.get('scope', 'this_only')
        
        deleted_count = 0
        
        if scope == 'all':
            # Delete entire series
            parent = job if job.is_recurring_parent else job.recurrence_parent
            if parent:
                # Count instances before deleting
                deleted_count = parent.recurrence_instances.count()
                # Delete parent (CASCADE will delete instances)
                parent.delete()
                deleted_count += 1  # Include parent
            else:
                job.delete()
                deleted_count = 1
                
        elif scope in ('this_and_future', 'future'):
            # Delete this and all future instances
            if job.is_recurring_instance:
                parent = job.recurrence_parent
                if parent:
                    # Delete current and future instances
                    deleted_count = parent.delete_recurring_instances(
                        after_date=job.recurrence_original_start
                    )
                else:
                    job.delete()
                    deleted_count = 1
            elif job.is_recurring_parent:
                # If this is the parent, delete all instances
                deleted_count = job.recurrence_instances.count()
                job.recurrence_instances.all().delete()
                job.recurrence_rule = None
                job.save()
            else:
                job.delete()
                deleted_count = 1
                
        else:  # scope == 'this_only'
            job.delete()
            deleted_count = 1
        
        return JsonResponse({
            'status': 'success',
            'deleted_count': deleted_count,
            'scope': scope,
        })
        
    except Exception as e:
        print(f"DEBUG: Error deleting job: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)


def _format_job_response(job):
    """
    Format a Job instance for JSON response.
    """
    # Format dates for FullCalendar
    if job.all_day:
        start_str = timezone.localtime(job.start_dt).date().isoformat()
        end_str = timezone.localtime(job.end_dt).date().isoformat()
    else:
        # Use strftime to avoid timezone offset in ISO string
        start_str = timezone.localtime(job.start_dt).strftime('%Y-%m-%dT%H:%M:%S')
        end_str = timezone.localtime(job.end_dt).strftime('%Y-%m-%dT%H:%M:%S')
    
    response = {
        'id': job.id,
        'business_name': job.business_name,
        'contact_name': job.contact_name,
        'phone': job.phone,
        'address_line1': job.address_line1,
        'address_line2': job.address_line2,
        'city': job.city,
        'state': job.state,
        'postal_code': job.postal_code,
        'trailer_color': job.trailer_color,
        'trailer_serial': job.trailer_serial,
        'trailer_details': job.trailer_details,
        'start': start_str,
        'end': end_str,
        'allDay': job.all_day,
        'status': job.status,
        'notes': job.notes,
        'repair_notes': job.repair_notes,
        'repeat_type': job.repeat_type,
        'repeat_n_months': job.repeat_n_months,
        'quote': job.quote if job.quote else '',
        # Recurring event info
        'is_recurring_parent': job.is_recurring_parent,
        'is_recurring_instance': job.is_recurring_instance,
        'recurrence_parent_id': job.recurrence_parent_id,
        'recurrence_rule': job.recurrence_rule,
    }
    
    return response

