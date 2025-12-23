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
from rental_scheduler.constants import MIN_VALID_YEAR, MAX_VALID_YEAR, MAX_JOB_SPAN_DAYS


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
                
                # Check for "forever" series
                is_forever = recurrence.get('end') == 'never' or recurrence.get('forever', False)
                
                # If neither count nor until_date is provided and no explicit 'end' mode, default to forever
                if not is_forever and not count and not until_date_str:
                    is_forever = True
                
                # Validate count if provided
                if count and not is_forever:
                    count_int = int(count)
                    if count_int > 500:
                        return JsonResponse({'error': 'Recurrence count cannot exceed 500 occurrences.'}, status=400)
                
                # Parse until_date if provided
                until_date = None
                if until_date_str and not is_forever:
                    try:
                        until_date = timezone.make_aware(datetime.fromisoformat(until_date_str))
                    except (ValueError, TypeError):
                        pass
                
                # Create recurrence rule
                job.create_recurrence_rule(
                    recurrence_type=recur_type,
                    interval=interval,
                    count=int(count) if count and not is_forever else None,
                    until_date=until_date
                )
                
                # Store 'end' flag for forever series
                if is_forever:
                    rule = job.recurrence_rule or {}
                    rule['end'] = 'never'
                    job.recurrence_rule = rule
                    job.save(update_fields=['recurrence_rule'])
                    print(f"DEBUG: Created forever recurring job {job.id}")
                else:
                    # Generate recurring instances for non-forever series
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
    Soft delete a job with scope support for recurring events.
    
    POST /api/jobs/<pk>/delete-recurring/
    Body: {"delete_scope": "this_only" | "this_and_future" | "all"}
    
    Scopes:
    - this_only: Soft delete only this job (default)
    - all: Soft delete entire series (parent + all instances)
    - this_and_future: Soft delete this and all future instances, truncate recurrence generation
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
            # Soft delete entire series
            parent = job if job.is_recurring_parent else job.recurrence_parent
            if parent:
                # Count non-deleted instances before deleting
                deleted_count = parent.recurrence_instances.filter(is_deleted=False).count()
                # Soft delete all instances
                parent.recurrence_instances.filter(is_deleted=False).update(is_deleted=True)
                # Soft delete parent
                if not parent.is_deleted:
                    parent.is_deleted = True
                    parent.save(update_fields=['is_deleted'])
                    deleted_count += 1  # Include parent
            else:
                # Non-recurring job
                if not job.is_deleted:
                    job.is_deleted = True
                    job.save(update_fields=['is_deleted'])
                    deleted_count = 1
                
        elif scope in ('this_and_future', 'future'):
            # Delete this and all future instances
            if job.is_recurring_instance:
                parent = job.recurrence_parent
                if parent:
                    # Soft delete current and future instances
                    from datetime import timedelta
                    from rental_scheduler.utils.recurrence import delete_recurring_instances
                    deleted_count = delete_recurring_instances(
                        parent,
                        after_date=job.recurrence_original_start
                    )
                    
                    # Truncate virtual occurrences by setting end_recurrence_date
                    # Set to day before the deleted boundary
                    truncate_date = job.recurrence_original_start.date() - timedelta(days=1)
                    parent.end_recurrence_date = truncate_date
                    parent.save(update_fields=['end_recurrence_date'])
                else:
                    # Orphaned instance - just soft delete it
                    if not job.is_deleted:
                        job.is_deleted = True
                        job.save(update_fields=['is_deleted'])
                        deleted_count = 1
                        
            elif job.is_recurring_parent:
                # If this is the parent, delete all instances and truncate at parent date
                deleted_count = job.recurrence_instances.filter(is_deleted=False).count()
                job.recurrence_instances.filter(is_deleted=False).update(is_deleted=True)
                
                # Truncate recurrence generation so it ends after the parent occurrence
                job.end_recurrence_date = job.start_dt.date()
                job.save(update_fields=['end_recurrence_date'])
                # Keep parent itself not deleted
            else:
                # Non-recurring job
                if not job.is_deleted:
                    job.is_deleted = True
                    job.save(update_fields=['is_deleted'])
                    deleted_count = 1
                
        else:  # scope == 'this_only'
            # Guard: Don't allow deleting only the parent (would orphan the series)
            if job.is_recurring_parent and job.recurrence_instances.exists():
                return JsonResponse({
                    'status': 'error',
                    'error': 'Cannot delete only the series template. Choose to delete the entire series or delete this and future events.'
                }, status=400)
            
            # Soft delete single job
            if not job.is_deleted:
                job.is_deleted = True
                job.save(update_fields=['is_deleted'])
                deleted_count = 1
        
        return JsonResponse({
            'success': True,
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


@require_http_methods(["POST"])
@csrf_protect
def materialize_occurrence_api(request):
    """
    Materialize a virtual occurrence into a real Job row.
    
    This is called when a user interacts with a virtual occurrence (edit, complete, etc.)
    and we need to create a real Job instance for it.
    
    POST /api/recurrence/materialize/
    {
        "parent_id": 123,
        "original_start": "2026-02-20T10:00:00"
    }
    
    Returns:
    {
        "job_id": 456,
        "created": true,  // false if already existed
        "job": { ... }    // full job data
    }
    """
    try:
        data = json.loads(request.body)
        
        parent_id = data.get('parent_id')
        original_start = data.get('original_start')
        
        if not parent_id:
            return JsonResponse({'error': 'parent_id is required'}, status=400)
        if not original_start:
            return JsonResponse({'error': 'original_start is required'}, status=400)
        
        # Get the parent job
        parent = get_object_or_404(Job, pk=parent_id)
        
        # Verify it's a recurring parent
        if not parent.is_recurring_parent:
            return JsonResponse({
                'error': 'Job is not a recurring parent'
            }, status=400)
        
        # Materialize the occurrence
        from rental_scheduler.utils.recurrence import materialize_occurrence
        
        job, created = materialize_occurrence(parent, original_start)
        
        # Return the job data
        response_data = {
            'job_id': job.id,
            'created': created,
            'job': _format_job_response(job),
        }
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def recurrence_preview_occurrences(request):
    """
    Return HTML fragment with the next N virtual occurrences for a forever recurring parent.
    
    Query params:
        parent_id: int - ID of the recurring parent job
        count: int - Number of occurrences to preview (default 5, max 200)
    
    Returns HTML rows suitable for insertion into a job table.
    """
    from django.shortcuts import render
    from django.utils import timezone
    from datetime import timedelta
    from rental_scheduler.utils.recurrence import is_forever_series, generate_occurrences_in_window
    from rental_scheduler.utils.phone import format_phone
    
    MAX_PREVIEW_COUNT = 200
    
    parent_id = request.GET.get('parent_id')
    count = request.GET.get('count', '5')
    
    if not parent_id:
        return JsonResponse({'error': 'parent_id is required'}, status=400)
    
    try:
        parent_id = int(parent_id)
        count = min(int(count), MAX_PREVIEW_COUNT)  # Cap at 200 to prevent abuse
    except ValueError:
        return JsonResponse({'error': 'Invalid parent_id or count'}, status=400)
    
    try:
        parent = Job.objects.select_related('calendar').get(pk=parent_id, is_deleted=False)
    except Job.DoesNotExist:
        return JsonResponse({'error': 'Job not found'}, status=404)
    
    # Verify this is a forever recurring parent
    if parent.recurrence_parent is not None:
        return JsonResponse({'error': 'This is a recurring instance, not a parent'}, status=400)
    
    if not is_forever_series(parent):
        return JsonResponse({'error': 'This job is not a forever recurring series'}, status=400)
    
    # Generate upcoming occurrences starting from today
    today = timezone.localdate()
    # Look ahead enough to get the requested count (generous window based on recurrence type)
    rule = parent.recurrence_rule or {}
    recurrence_type = rule.get('type', 'monthly')
    interval = rule.get('interval', 1)
    
    # Calculate a reasonable window based on recurrence type
    if recurrence_type == 'daily':
        window_days = count * interval + 30
    elif recurrence_type == 'weekly':
        window_days = count * interval * 7 + 30
    elif recurrence_type == 'monthly':
        window_days = count * interval * 31 + 60
    else:  # yearly
        window_days = count * interval * 366 + 60
    
    window_end = today + timedelta(days=window_days)
    
    # Generate occurrences
    occurrences = generate_occurrences_in_window(
        parent,
        today,
        window_end,
        safety_cap=count + 10  # A few extra in case some are materialized
    )
    
    # Get already-materialized instance starts for this parent
    materialized_starts = set(
        Job.objects.filter(
            recurrence_parent=parent
        ).values_list('recurrence_original_start', flat=True)
    )
    
    # Filter out parent and already-materialized occurrences
    virtual_occurrences = []
    for occ in occurrences:
        if occ.get('is_parent'):
            continue
        if occ['start_dt'] in materialized_starts:
            continue
        virtual_occurrences.append(occ)
        if len(virtual_occurrences) >= count:
            break
    
    # For forever series, show "more" button until we hit the max
    has_more = count < MAX_PREVIEW_COUNT
    
    # Build context for template
    context = {
        'parent': parent,
        'occurrences': virtual_occurrences,
        'count': count,
        'has_more': has_more,
        'format_phone': format_phone,
    }
    
    return render(request, 'rental_scheduler/partials/virtual_occurrence_rows.html', context)