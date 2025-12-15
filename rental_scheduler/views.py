"""
Views for the rental scheduler application.

Optimized for performance:
- Queries use select_related/prefetch_related to avoid N+1
- Calendar feed endpoint is read-only (no DB writes)
- Payloads minimized with .only() where appropriate
"""
import json
import logging
import re
from datetime import date, datetime, timedelta

from django import forms
from django.contrib import messages
from django.db import models, transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from rental_scheduler.utils.ai_parser import parse_description_with_ai
from rental_scheduler.utils.events import (
    event_to_calendar_json,
    get_call_reminder_sunday,
    normalize_event_datetimes,
)

from .forms import CalendarImportForm, JobForm, WorkOrderForm, WorkOrderLineForm
from .models import Calendar, Invoice, Job, WorkOrder

logger = logging.getLogger(__name__)

# HTML5 datetime-local format constant
DATETIME_LOCAL_FMT = "%Y-%m-%dT%H:%M"
# HTML5 date-only format (used when All Day is checked)
DATE_ONLY_FMT = "%Y-%m-%d"

class HomeView(TemplateView):
    template_name = 'rental_scheduler/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'GTS Rental Scheduler'
        return context


class CalendarView(TemplateView):
    """Main calendar view for displaying jobs"""
    template_name = 'rental_scheduler/calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Calendar'
        
        # Serialize calendars for JavaScript
        calendars = Calendar.objects.filter(is_active=True)
        context['calendars'] = [
            {'id': cal.id, 'name': cal.name, 'color': cal.color}
            for cal in calendars
        ]
        
        # Also add as JSON string for debugging
        context['calendars_json'] = json.dumps(context['calendars'])
        
        # Add guardrails for frontend date validation (single source of truth)
        from rental_scheduler.constants import get_guardrails_for_frontend
        context['guardrails_json'] = json.dumps(get_guardrails_for_frontend())
        
        # Add timestamp for cache busting
        import time
        context['timestamp'] = int(time.time())
        
        return context

# Calendar CRUD Views
class CalendarListView(ListView):
    """List all calendars with basic CRUD operations"""
    model = Calendar
    template_name = 'rental_scheduler/calendars/calendar_list.html'
    context_object_name = 'calendars'
    ordering = ['name']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Calendars'
        return context

class CalendarCreateView(CreateView):
    """Create a new calendar"""
    model = Calendar
    template_name = 'rental_scheduler/calendars/calendar_form.html'
    fields = ['name', 'color', 'call_reminder_color', 'is_active']
    success_url = reverse_lazy('rental_scheduler:calendar_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Calendar'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Calendar "{form.instance.name}" created successfully.')
        return super().form_valid(form)

class CalendarUpdateView(UpdateView):
    """Update an existing calendar"""
    model = Calendar
    template_name = 'rental_scheduler/calendars/calendar_form.html'
    fields = ['name', 'color', 'call_reminder_color', 'is_active']
    success_url = reverse_lazy('rental_scheduler:calendar_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Calendar: {self.object.name}'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Calendar "{form.instance.name}" updated successfully.')
        return super().form_valid(form)

class CalendarDeleteView(DeleteView):
    """Delete a calendar"""
    model = Calendar
    template_name = 'rental_scheduler/calendars/calendar_confirm_delete.html'
    success_url = reverse_lazy('rental_scheduler:calendar_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Delete Calendar: {self.object.name}'
        return context
    
    def delete(self, request, *args, **kwargs):
        calendar = self.get_object()
        messages.success(request, f'Calendar "{calendar.name}" deleted successfully.')
        return super().delete(request, *args, **kwargs)


# Job CRUD Views
class JobListView(ListView):
    """List all jobs with filtering, search, and sorting capabilities"""
    model = Job
    template_name = 'rental_scheduler/jobs/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 25
    
    def get_queryset(self):
        """Filter and sort jobs based on query parameters"""
        queryset = Job.objects.select_related('calendar').filter(is_deleted=False)
        
        # Calendar filter
        calendars = self.request.GET.getlist('calendars')
        if calendars:
            queryset = queryset.filter(calendar_id__in=calendars)
        
        # Date filter
        date_filter = self.request.GET.get('date_filter', 'all')
        if date_filter == 'custom':
            start_date = self.request.GET.get('start_date')
            end_date = self.request.GET.get('end_date')
            if start_date:
                try:
                    start_date_obj = timezone.datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=timezone.get_current_timezone())
                    queryset = queryset.filter(start_dt__gte=start_date_obj)
                except ValueError:
                    pass
            if end_date:
                try:
                    end_date_obj = timezone.datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, tzinfo=timezone.get_current_timezone())
                    queryset = queryset.filter(start_dt__lte=end_date_obj)
                except ValueError:
                    pass
        elif date_filter == 'future':
            now = timezone.now()
            queryset = queryset.filter(start_dt__gte=now)
        
        # Unified search across multiple fields with word-based matching
        search = self.request.GET.get('search', '').strip()
        if search:
            # Split search query into individual words
            search_words = search.split()
            
            # For each word, create a Q object that searches across all fields
            for word in search_words:
                word_query = models.Q(business_name__icontains=word) | \
                             models.Q(contact_name__icontains=word) | \
                             models.Q(phone__icontains=word) | \
                             models.Q(address_line1__icontains=word) | \
                             models.Q(address_line2__icontains=word) | \
                             models.Q(city__icontains=word) | \
                             models.Q(state__icontains=word) | \
                             models.Q(trailer_color__icontains=word) | \
                             models.Q(trailer_serial__icontains=word) | \
                             models.Q(trailer_details__icontains=word) | \
                             models.Q(notes__icontains=word) | \
                             models.Q(repair_notes__icontains=word)
                
                # Chain with AND logic - all words must match
                queryset = queryset.filter(word_query)
        
        # Sorting
        sort_by = self.request.GET.get('sort', '-start_dt')
        sort_direction = self.request.GET.get('direction', 'desc')
        
        # Validate sort field
        allowed_sort_fields = {
            'start_dt': 'start_dt',
            'end_dt': 'end_dt',
            'business_name': 'business_name',
            'contact_name': 'contact_name',
            'status': 'status',
            'calendar__name': 'calendar__name',
            'repeat_type': 'repeat_type',
        }
        
        if sort_by in allowed_sort_fields:
            sort_field = allowed_sort_fields[sort_by]
            if sort_direction == 'desc':
                sort_field = f'-{sort_field}'
            queryset = queryset.order_by(sort_field)
        else:
            # Default sorting
            queryset = queryset.order_by('-start_dt')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Jobs'
        
        # Add sorting context
        context['current_sort'] = self.request.GET.get('sort', 'start_dt')
        context['current_direction'] = self.request.GET.get('direction', 'desc')
        
        # Add search filter context for maintaining state
        context['search_query'] = self.request.GET.get('search', '')
        
        # Add calendar filter context
        from .models import Calendar
        context['calendars'] = Calendar.objects.all().order_by('name')
        
        # Get selected calendars
        selected_calendars = self.request.GET.getlist('calendars')
        context['selected_calendars'] = [int(cal_id) for cal_id in selected_calendars if cal_id.isdigit()]
        
        # Add date filter context
        context['date_filter'] = self.request.GET.get('date_filter', 'all')
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')
        
        return context


class JobForm(forms.ModelForm):
    """Custom form for Job creation with proper datetime handling"""
    
    # Override datetime fields to use proper widgets
    start_dt = forms.DateTimeField(
        required=True,
        input_formats=[DATETIME_LOCAL_FMT, DATE_ONLY_FMT],
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none',
            'required': True
        }, format=DATETIME_LOCAL_FMT),
        help_text="Start date and time of the job"
    )
    
    end_dt = forms.DateTimeField(
        required=True,
        input_formats=[DATETIME_LOCAL_FMT, DATE_ONLY_FMT],
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none',
            'required': True
        }, format=DATETIME_LOCAL_FMT),
        help_text="End date and time of the job"
    )
    
    date_call_received = forms.DateTimeField(
        required=False,
        input_formats=[DATETIME_LOCAL_FMT, DATE_ONLY_FMT],
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none'
        }, format=DATETIME_LOCAL_FMT),
        help_text="Date and time the initial call was received"
    )
    
    # Override the calendar field to make it visible
    calendar = forms.ModelChoiceField(
        queryset=Calendar.objects.filter(is_active=True),
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:border-gray-400 focus:outline-none',
            'required': True
        }),
        help_text="Select which calendar this event belongs to"
    )
    
    status = forms.ChoiceField(
        choices=[
            ('uncompleted', 'Uncompleted'),
            ('completed', 'Completed'),
        ],
        required=False,
        widget=forms.HiddenInput(),
        initial='uncompleted'
    )

    class Meta:
        model = Job
        fields = [
            'business_name', 'date_call_received', 'contact_name', 'phone',
            'address_line1', 'address_line2', 'city', 'state', 'postal_code',
            'start_dt', 'end_dt', 'all_day', 'repeat_type', 'notes',
            'trailer_color', 'trailer_serial', 'trailer_details', 'repair_notes', 'quote',
            'calendar', 'status'
        ]
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none'}),
            'contact_name': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none'}),
            'phone': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none'}),
            'address_line1': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none'}),
            'address_line2': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none'}),
            'city': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none'}),
            'state': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none'}),
            'postal_code': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none'}),
            'all_day': forms.CheckboxInput(attrs={'class': 'h-4 w-4 rounded border-gray-300 mr-2'}),
            'repeat_type': forms.Select(attrs={'class': 'w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:border-gray-400 focus:outline-none'}),
            'notes': forms.Textarea(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none h-20 resize-none', 'rows': 3}),
            'trailer_color': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none'}),
            'trailer_serial': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none'}),
            'trailer_details': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none'}),
            'repair_notes': forms.Textarea(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none h-32 resize-none', 'rows': 5}),
            'quote': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 pl-7 pr-3 py-2 text-sm focus:border-gray-400 focus:outline-none', 'placeholder': 'e.g., 500.00 or TBD'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-fill existing values with correct format so the browser control shows them
        for name in ("start_dt", "end_dt", "date_call_received"):
            if self.instance and getattr(self.instance, name, None):
                self.fields[name].initial = getattr(self.instance, name).strftime(DATETIME_LOCAL_FMT)
    
    def clean(self):
        """Custom validation to ensure end date is after start date and handle all-day normalization"""
        from datetime import datetime, time, timedelta
        
        cleaned_data = super().clean()
        all_day = cleaned_data.get("all_day") or False
        start_dt = cleaned_data.get("start_dt")
        end_dt = cleaned_data.get("end_dt")
        
        if not start_dt or not end_dt:
            raise forms.ValidationError("Please select both start and end dates.")
        
        if all_day:
            # Normalize to noon to avoid timezone shift issues
            start_normalized = datetime.combine(start_dt.date(), time(12, 0, 0))
            end_normalized = datetime.combine(end_dt.date(), time(12, 0, 0))
            
            # Make timezone-aware if using timezone support
            from django.utils import timezone
            if timezone.is_aware(start_dt):
                start_normalized = timezone.make_aware(start_normalized)
                end_normalized = timezone.make_aware(end_normalized)
            
            # For all-day events, allow same day (equal dates) but not end before start
            if start_normalized > end_normalized:
                self.add_error("end_dt", "End date cannot be before start date.")
            
            cleaned_data['start_dt'] = start_normalized
            cleaned_data['end_dt'] = end_normalized
        else:
            # Keep times as provided, just validate order
            # For timed events, end must be strictly after start
            if end_dt <= start_dt:
                self.add_error("end_dt", "End date/time must be after start date/time.")
        
        return cleaned_data


class JobDeleteView(DeleteView):
    """Delete a job"""
    model = Job
    template_name = 'rental_scheduler/jobs/job_confirm_delete.html'
    success_url = reverse_lazy('rental_scheduler:job_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Delete Job: {self.object.get_display_name()}'
        return context
    
    def delete(self, request, *args, **kwargs):
        job = self.get_object()
        messages.success(request, f'Job for {job.get_display_name()} deleted successfully.')
        return super().delete(request, *args, **kwargs)


# Print Views
@method_decorator(xframe_options_exempt, name='dispatch')
class JobPrintWOView(DetailView):
    """Print work order view"""
    model = Job
    template_name = 'rental_scheduler/jobs/job_print_wo.html'
    context_object_name = 'job'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Work Order'
        return context


@method_decorator(xframe_options_exempt, name='dispatch')
class JobPrintWOCustomerView(DetailView):
    """Print customer copy work order view"""
    model = Job
    template_name = 'rental_scheduler/jobs/job_print_wo_customer.html'
    context_object_name = 'job'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Customer Work Order'
        return context


@method_decorator(xframe_options_exempt, name='dispatch')
class JobPrintInvoiceView(DetailView):
    """Print invoice view"""
    model = Job
    template_name = 'rental_scheduler/jobs/job_print_invoice.html'
    context_object_name = 'job'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Invoice'
        return context


# Calendar API Views
def lighten_color(hex_color, factor):
    """
    Lighten a hex color by a given factor (0-1).
    Factor of 0.3 means 30% lighter.
    """
    # Remove # if present
    hex_color = hex_color.lstrip('#')
    
    # Convert to RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    # Lighten by mixing with white
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    
    # Convert back to hex
    return f"#{r:02x}{g:02x}{b:02x}"

def get_job_calendar_data(request):
    """API endpoint to get job data for calendar display"""
    from rental_scheduler.constants import MAX_MULTI_DAY_EXPANSION_DAYS
    
    try:
        # Get date range from request
        start_date = request.GET.get('start')
        end_date = request.GET.get('end')
        
        # Parse request window dates for clamping multi-day expansions
        request_start_date = None
        request_end_date = None
        if start_date:
            try:
                # Handle ISO format with timezone: "2025-01-01T00:00:00-05:00"
                if 'T' in start_date:
                    request_start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00')).date()
                else:
                    request_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            except (ValueError, TypeError) as e:
                logger.warning(f"Could not parse start_date '{start_date}': {e}")
        if end_date:
            try:
                if 'T' in end_date:
                    request_end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00')).date()
                else:
                    request_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except (ValueError, TypeError) as e:
                logger.warning(f"Could not parse end_date '{end_date}': {e}")
        
        # Get filter parameters
        status_filter = request.GET.get('status')
        calendar_filter = request.GET.get('calendar')
        search_filter = request.GET.get('search')
        
        # Build queryset - optimized to select only necessary fields for calendar display
        # Prefetch call_reminders to avoid N+1 queries
        jobs = Job.objects.select_related('calendar').prefetch_related('call_reminders').filter(is_deleted=False).only(
            'id', 'business_name', 'contact_name', 'phone', 'status',
            'start_dt', 'end_dt', 'all_day', 'trailer_color',
            'has_call_reminder', 'call_reminder_weeks_prior', 'call_reminder_completed',
            'recurrence_rule', 'recurrence_parent_id',
            'calendar__id', 'calendar__name', 'calendar__color', 'calendar__call_reminder_color'
        )
        
        # Apply date range filter using timezone-aware datetime bounds
        if request_start_date and request_end_date:
            # Build aware datetime bounds in project timezone
            # start of first day for end_dt comparison
            filter_start_dt = timezone.make_aware(
                datetime.combine(request_start_date, datetime.min.time())
            )
            # end of last day for start_dt comparison (use start of next day as exclusive bound)
            filter_end_dt = timezone.make_aware(
                datetime.combine(request_end_date + timedelta(days=1), datetime.min.time())
            )
            jobs = jobs.filter(
                start_dt__lt=filter_end_dt,
                end_dt__gte=filter_start_dt
            )
        
        # Apply status filter
        if status_filter:
            jobs = jobs.filter(status=status_filter)
        
        # Apply calendar filter (supports multiple calendar IDs as comma-separated string)
        if calendar_filter:
            # Check if it's a comma-separated list of IDs
            if ',' in calendar_filter:
                calendar_ids = [int(cid.strip()) for cid in calendar_filter.split(',') if cid.strip().isdigit()]
                if calendar_ids:
                    jobs = jobs.filter(calendar_id__in=calendar_ids)
            else:
                # Single calendar ID
                jobs = jobs.filter(calendar_id=calendar_filter)
        
        # Apply search filter
        if search_filter:
            jobs = jobs.filter(
                models.Q(business_name__icontains=search_filter) |
                models.Q(contact_name__icontains=search_filter) |
                models.Q(phone__icontains=search_filter) |
                models.Q(trailer_color__icontains=search_filter) |
                models.Q(trailer_serial__icontains=search_filter) |
                models.Q(trailer_details__icontains=search_filter) |
                models.Q(notes__icontains=search_filter) |
                models.Q(repair_notes__icontains=search_filter)
            )
        
        # Convert to calendar events
        events = []
        
        for job in jobs:
            # Format phone number to match dialog format: (123) 456-5875
            phone_formatted = ""
            if job.get_phone():
                # Strip all non-digit characters first
                phone_digits = ''.join(filter(str.isdigit, job.get_phone()))
                if phone_digits:
                    if len(phone_digits) == 10:
                        phone_formatted = f"({phone_digits[:3]}) {phone_digits[3:6]}-{phone_digits[6:]}"
                    else:
                        phone_formatted = phone_digits
                else:
                    # If no digits found, use the original value
                    phone_formatted = job.get_phone()
            
            # Build the event title in format: Business Name (Contact Name) - Phone Number
            business_name = job.business_name or ""
            contact_name = job.contact_name or ""
            
            if business_name and contact_name:
                title = f"{business_name} ({contact_name})"
            elif business_name:
                title = business_name
            elif contact_name:
                title = contact_name
            else:
                title = "No Name Provided"
            
            if phone_formatted:
                title += f" - {phone_formatted}"
            
            # Get calendar color and apply lighter shade for completed jobs
            calendar_color = job.calendar.color if job.calendar.color else '#3B82F6'
            if job.status == 'completed':
                # Create a lighter shade for completed events
                calendar_color = lighten_color(calendar_color, 0.3)
            
            # Calculate the date span of this job
            job_start_local = timezone.localtime(job.start_dt)
            job_end_local = timezone.localtime(job.end_dt)
            
            # Determine if this is a multi-day job
            job_start_date = job_start_local.date()
            job_end_date = job_end_local.date()
            is_multi_day = (job_end_date > job_start_date)
            
            if is_multi_day:
                # Break multi-day jobs into separate events for each day
                # CLAMP to request window to prevent runaway responses from bad data
                total_days = (job_end_date - job_start_date).days
                
                # Determine the visible portion of this job within the request window
                if request_start_date and request_end_date:
                    visible_start = max(job_start_date, request_start_date)
                    visible_end = min(job_end_date, request_end_date)
                else:
                    # No window specified, but still apply safety cap
                    visible_start = job_start_date
                    visible_end = job_end_date
                
                # Safety cap: never expand more than MAX_MULTI_DAY_EXPANSION_DAYS
                visible_span = (visible_end - visible_start).days
                if visible_span > MAX_MULTI_DAY_EXPANSION_DAYS:
                    logger.warning(
                        f"Job {job.id} visible span ({visible_span} days) exceeds max; "
                        f"capping to {MAX_MULTI_DAY_EXPANSION_DAYS} days"
                    )
                    visible_end = visible_start + timedelta(days=MAX_MULTI_DAY_EXPANSION_DAYS)
                
                # Skip if job is entirely outside the visible window
                if visible_start > visible_end:
                    continue
                
                current_date = visible_start
                day_number = (visible_start - job_start_date).days  # Track actual day number in the job
                
                while current_date <= visible_end:
                    # For all-day events, use date strings
                    # For timed events, use the actual times on first/last day, full day for middle days
                    if job.all_day:
                        # All-day event: use noon to avoid timezone shifting issues
                        day_start = current_date.strftime('%Y-%m-%dT12:00:00')
                        day_end = (current_date + timedelta(days=1)).strftime('%Y-%m-%dT12:00:00')  # Exclusive end
                        is_all_day = True
                    else:
                        # Timed event: first day starts at job time, last day ends at job time, middle days are full days
                        if current_date == job_start_date and current_date == job_end_date:
                            # Single day (shouldn't happen in multi-day branch, but handle it)
                            day_start = job_start_local.strftime('%Y-%m-%dT%H:%M:%S')
                            day_end = job_end_local.strftime('%Y-%m-%dT%H:%M:%S')
                            is_all_day = False
                        elif current_date == job_start_date:
                            # First day: start at job start time, end at midnight
                            day_start = job_start_local.strftime('%Y-%m-%dT%H:%M:%S')
                            day_end = (current_date + timedelta(days=1)).strftime('%Y-%m-%dT00:00:00')
                            is_all_day = False
                        elif current_date == job_end_date:
                            # Last day: start at midnight, end at job end time
                            day_start = current_date.strftime('%Y-%m-%dT00:00:00')
                            day_end = job_end_local.strftime('%Y-%m-%dT%H:%M:%S')
                            is_all_day = False
                        else:
                            # Middle day: full day from midnight to midnight
                            day_start = current_date.strftime('%Y-%m-%dT00:00:00')
                            day_end = (current_date + timedelta(days=1)).strftime('%Y-%m-%dT00:00:00')
                            is_all_day = False
                    
                    # Create event for this day - LEAN payload (details fetched on click)
                    day_event = {
                        'id': f"job-{job.id}-day-{day_number}",
                        'title': title,
                        'start': day_start,
                        'end': day_end,
                        'allDay': is_all_day,
                        'backgroundColor': calendar_color,
                        'borderColor': calendar_color,
                        'extendedProps': {
                            'type': 'job',
                            'job_id': job.id,
                            'status': job.status,
                            'calendar_id': job.calendar.id,
                            'calendar_name': job.calendar.name,
                            # Minimal info for tooltip/display
                            'phone': job.get_phone(),
                            'trailer_color': job.trailer_color,
                            # Recurring flags only (not full rule object)
                            'is_recurring_parent': job.is_recurring_parent,
                            'is_recurring_instance': job.is_recurring_instance,
                            # Multi-day tracking
                            'is_multi_day': True,
                            'multi_day_number': day_number,
                            'multi_day_total': total_days,
                            # Store full job date range for display
                            'job_start_date': job_start_date.isoformat(),
                            'job_end_date': job_end_date.isoformat(),
                        }
                    }
                    
                    events.append(day_event)
                    current_date += timedelta(days=1)
                    day_number += 1
            else:
                # Single-day job: use the original approach - LEAN payload (details fetched on click)
                event = event_to_calendar_json(
                    job,
                    title=title,
                    backgroundColor=calendar_color,
                    borderColor=calendar_color,
                    extendedProps={
                        'type': 'job',
                        'job_id': job.id,
                        'status': job.status,
                        'calendar_id': job.calendar.id,
                        'calendar_name': job.calendar.name,
                        # Minimal info for tooltip/display
                        'phone': job.get_phone(),
                        'trailer_color': job.trailer_color,
                        # Recurring flags only (not full rule object)
                        'is_recurring_parent': job.is_recurring_parent,
                        'is_recurring_instance': job.is_recurring_instance,
                        # Multi-day tracking
                        'is_multi_day': False,
                    }
                )
                
                # Override the id to use the "job-{id}" format
                event['id'] = f"job-{job.id}"
                
                events.append(event)
            
            # Create call reminder event if enabled and not completed
            if job.has_call_reminder and job.call_reminder_weeks_prior and not job.call_reminder_completed:
                try:
                    reminder_dt = get_call_reminder_sunday(job.start_dt, job.call_reminder_weeks_prior)
                    reminder_end_dt = reminder_dt + timedelta(days=1)  # All-day event (exclusive end)
                    
                    # Get the call reminder color from the calendar
                    reminder_color = job.calendar.call_reminder_color or '#F59E0B'
                    
                    # Format the reminder title
                    reminder_title = f"📞 {title}"
                    
                    # Get the CallReminder notes from prefetched data (avoids N+1 query)
                    reminder_notes = ''
                    try:
                        # Use prefetched call_reminders to avoid extra DB query
                        call_reminders = list(job.call_reminders.all())
                        if call_reminders:
                            reminder_notes = call_reminders[0].notes or ''
                    except Exception:
                        pass
                    
                    reminder_event = {
                        'id': f"reminder-{job.id}",
                        'title': reminder_title,
                        'start': f"{reminder_dt.date().isoformat()}T12:00:00",
                        'end': f"{reminder_end_dt.date().isoformat()}T12:00:00",  # Exclusive end
                        'backgroundColor': reminder_color,
                        'borderColor': reminder_color,
                        'allDay': True,
                        'extendedProps': {
                            'type': 'call_reminder',
                            'job_id': job.id,
                            'status': job.status,
                            'calendar_id': job.calendar.id,
                            'calendar_name': job.calendar.name,
                            'business_name': job.business_name,
                            'contact_name': job.contact_name,
                            'phone': job.get_phone(),
                            'weeks_prior': job.call_reminder_weeks_prior,
                            'job_date': timezone.localtime(job.start_dt).date().isoformat(),
                            'call_reminder_completed': job.call_reminder_completed,
                            'notes': reminder_notes,
                        }
                    }
                    
                    events.append(reminder_event)
                except Exception as reminder_error:
                    logger.error(f"Error creating call reminder for job {job.id}: {str(reminder_error)}")
        
        # Fetch standalone CallReminder records (not linked to jobs)
        # Only query if we have valid date bounds (reuse already-parsed dates from top of function)
        if request_start_date and request_end_date:
            try:
                from .models import CallReminder
                
                # Parse calendar_ids for filter (reuse logic)
                reminder_calendar_ids = []
                if calendar_filter:
                    if ',' in calendar_filter:
                        reminder_calendar_ids = [int(cid.strip()) for cid in calendar_filter.split(',') if cid.strip().isdigit()]
                    else:
                        try:
                            reminder_calendar_ids = [int(calendar_filter)]
                        except ValueError:
                            pass
                
                # Build optimized query with .only() for minimal payload
                reminder_base_qs = CallReminder.objects.filter(
                    reminder_date__range=[request_start_date, request_end_date],
                    job__isnull=True,  # Only standalone reminders
                ).select_related('calendar').only(
                    'id', 'reminder_date', 'notes', 'completed',
                    'calendar__id', 'calendar__name', 'calendar__call_reminder_color', 'calendar__is_active'
                )
                
                if reminder_calendar_ids:
                    call_reminders = reminder_base_qs.filter(calendar_id__in=reminder_calendar_ids)
                else:
                    # No filter, get all active calendars
                    call_reminders = reminder_base_qs.filter(calendar__is_active=True)
                
                # Add standalone call reminders to events (read-only, no DB writes)
                for reminder in call_reminders:
                    try:
                        # Normalize reminder_date to date object in-memory only (no DB writes)
                        reminder_date = reminder.reminder_date
                        
                        # Handle datetime objects (defensive - shouldn't happen with DateField)
                        if isinstance(reminder_date, datetime):
                            reminder_date = reminder_date.date()
                        # Handle string objects (defensive - shouldn't happen with DateField)
                        elif isinstance(reminder_date, str):
                            reminder_date = datetime.strptime(reminder_date[:10], '%Y-%m-%d').date()
                        
                        reminder_color = reminder.calendar.call_reminder_color or '#F59E0B'
                        
                        # Apply lighter shade for completed reminders
                        if reminder.completed:
                            reminder_color = lighten_color(reminder_color, 0.3)
                        
                        reminder_end_dt = reminder_date + timedelta(days=1)
                        
                        # Build title with notes if available
                        reminder_title = "📞 Call Reminder"
                        if reminder.notes:
                            # Truncate notes if too long for display
                            notes_preview = reminder.notes[:50] + '...' if len(reminder.notes) > 50 else reminder.notes
                            reminder_title = f"📞 {notes_preview}"
                        
                        # Add completion indicator to title for completed reminders
                        if reminder.completed:
                            reminder_title = f"✓ {reminder_title}"
                        
                        reminder_event = {
                            'id': f"call-reminder-{reminder.id}",
                            'title': reminder_title,
                            'start': f"{reminder_date.isoformat()}T12:00:00",
                            'end': f"{reminder_end_dt.isoformat()}T12:00:00",  # Exclusive end for all-day event
                            'backgroundColor': reminder_color,
                            'borderColor': reminder_color,
                            'allDay': True,
                            'extendedProps': {
                                'type': 'standalone_call_reminder',
                                'reminder_id': reminder.id,
                                'calendar_id': reminder.calendar.id,
                                'calendar_name': reminder.calendar.name,
                                'notes': reminder.notes,
                                'completed': reminder.completed,
                                'reminder_date': reminder_date.isoformat(),
                            }
                        }
                        
                        events.append(reminder_event)
                    except Exception as single_reminder_error:
                        logger.error(f"Error processing call reminder {reminder.id}: {str(single_reminder_error)}")
                        # Skip this reminder and continue with others
            except Exception as reminder_fetch_error:
                logger.error(f"Error fetching standalone call reminders: {str(reminder_fetch_error)}")
                # Continue without standalone reminders if there's an error
        
        return JsonResponse({
            'status': 'success',
            'events': events
        })
        
    except Exception as e:
        logger.error(f"Error getting calendar data: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@csrf_protect
def update_job_status(request, job_id):
    """API endpoint to update job status with CSRF protection"""
    try:
        job = get_object_or_404(Job, id=job_id)
        data = json.loads(request.body)
        new_status = data.get('status')
        
        if new_status not in dict(Job.STATUS_CHOICES):
            return JsonResponse({'error': 'Invalid status'}, status=400)
        
        old_status = job.status
        job.status = new_status
        job.save()
        
        return JsonResponse({
            'success': True,
            'old_status': old_status,
            'new_status': new_status,
            'is_canceled': False,  # No canceled status in simplified system
        })
        
    except Exception as e:
        logger.error(f"Error updating job status: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_protect
def mark_call_reminder_complete(request, job_id):
    """API endpoint to mark a call reminder as complete"""
    try:
        job = get_object_or_404(Job, id=job_id)
        job.call_reminder_completed = True
        job.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Call reminder marked as complete'
        })
        
    except Exception as e:
        logger.error(f"Error marking call reminder complete: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


def call_reminder_create_partial(request):
    """Return call reminder creation form partial for panel"""
    from .forms import CallReminderForm
    from datetime import datetime
    
    # Get date from query params and pre-fill form
    date_str = request.GET.get('date')
    calendar_id = request.GET.get('calendar')
    
    initial = {}
    if date_str:
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            initial['reminder_date'] = date_obj
        except ValueError:
            pass
    
    if calendar_id:
        try:
            initial['calendar'] = int(calendar_id)
        except (ValueError, TypeError):
            pass
    
    form = CallReminderForm(initial=initial)
    
    return render(request, 'rental_scheduler/call_reminders/_call_reminder_form_partial.html', {
        'form': form,
        'title': 'New Call Reminder'
    })


@require_http_methods(["POST"])
@csrf_protect
def call_reminder_create_submit(request):
    """Handle call reminder creation form submission"""
    from .forms import CallReminderForm
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("="*80)
    logger.info(f"Call reminder create request received")
    logger.info(f"POST data: {dict(request.POST)}")
    logger.info("="*80)
    
    form = CallReminderForm(request.POST)
    
    if form.is_valid():
        try:
            reminder = form.save()
            logger.info(f"Call reminder created successfully: ID={reminder.id}")
            
            return JsonResponse({
                'success': True,
                'message': 'Call reminder created successfully',
                'reminder_id': reminder.id
            })
        except Exception as e:
            logger.error(f"Error saving call reminder: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    else:
        logger.error(f"Form validation failed!")
        logger.error(f"Form errors: {form.errors}")
        
        return JsonResponse({
            'success': False,
            'errors': dict(form.errors)
        }, status=400)


@require_http_methods(["POST"])
@csrf_protect
def call_reminder_update(request, pk):
    """API endpoint to update call reminder notes and completion status"""
    import json
    from .models import CallReminder
    
    try:
        reminder = get_object_or_404(CallReminder, id=pk)
        
        # Parse JSON body
        data = json.loads(request.body)
        
        # Update notes if provided
        if 'notes' in data:
            reminder.notes = data['notes']
        
        # Update completed status if provided
        if 'completed' in data:
            completed = data['completed']
            if isinstance(completed, str):
                completed = completed.lower() in ('true', '1', 'yes', 'on')
            reminder.completed = bool(completed)
        
        reminder.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Call reminder updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating call reminder: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_protect
def call_reminder_delete(request, pk):
    """API endpoint to delete a call reminder"""
    from .models import CallReminder
    
    try:
        reminder = get_object_or_404(CallReminder, id=pk)
        reminder.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Call reminder deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting call reminder: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_protect
def job_call_reminder_update(request, job_id):
    """API endpoint to get or create and update CallReminder for a job"""
    import json
    from .models import CallReminder, Job
    from .utils.events import get_call_reminder_sunday
    
    try:
        job = get_object_or_404(Job, id=job_id)
        
        # Parse JSON body
        data = json.loads(request.body)
        
        # Calculate the reminder date based on job's settings
        if job.has_call_reminder and job.call_reminder_weeks_prior:
            reminder_date = get_call_reminder_sunday(job.start_dt, job.call_reminder_weeks_prior).date()
        else:
            return JsonResponse({'error': 'Job does not have call reminder enabled'}, status=400)
        
        # Get or create CallReminder for this job
        reminder, created = CallReminder.objects.get_or_create(
            job=job,
            calendar=job.calendar,
            defaults={'reminder_date': reminder_date, 'notes': ''}
        )
        
        # Update the reminder_date in case job date changed
        reminder.reminder_date = reminder_date
        
        # Update notes if provided
        if 'notes' in data:
            reminder.notes = data['notes']
        
        # Update completed status if provided
        if 'completed' in data:
            completed = data['completed']
            if isinstance(completed, str):
                completed = completed.lower() in ('true', '1', 'yes', 'on')
            reminder.completed = bool(completed)
            # Also update the job's call_reminder_completed flag
            job.call_reminder_completed = reminder.completed
            job.save(update_fields=['call_reminder_completed'])
        
        reminder.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Call reminder updated successfully',
            'reminder_id': reminder.id
        })
        
    except Exception as e:
        logger.error(f"Error updating job call reminder: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_protect
def delete_job_api(request, job_id):
    """API endpoint to delete a job with CSRF protection"""
    try:
        job = get_object_or_404(Job, id=job_id)
        job_name = job.get_display_name()
        
        # Soft delete by setting is_deleted flag
        job.is_deleted = True
        job.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Job for {job_name} deleted successfully.',
            'job_id': job_id
        })
        
    except Exception as e:
        logger.error(f"Error deleting job: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


# Work Order Views
class WorkOrderListView(ListView):
    """List all work orders with filtering, search, and sorting capabilities"""
    model = WorkOrder
    template_name = 'rental_scheduler/workorders/workorder_list.html'
    context_object_name = 'work_orders'
    paginate_by = 25
    
    def get_queryset(self):
        """Filter and sort work orders based on query parameters"""
        queryset = WorkOrder.objects.select_related('job__calendar').filter(job__is_deleted=False)
        
        # Filter by job status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(job__status=status)
        
        # Filter by calendar
        calendar_id = self.request.GET.get('calendar')
        if calendar_id:
            queryset = queryset.filter(job__calendar_id=calendar_id)
        
        # Search across multiple fields
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(wo_number__icontains=search) |
                models.Q(job__business_name__icontains=search) |
                models.Q(job__contact_name__icontains=search) |
                models.Q(job__phone__icontains=search) |
                models.Q(job__address_line1__icontains=search) |
                models.Q(job__city__icontains=search) |
                models.Q(job__trailer_color__icontains=search) |
                models.Q(job__trailer_serial__icontains=search) |
                models.Q(job__trailer_details__icontains=search) |
                models.Q(job__repair_notes__icontains=search) |
                models.Q(notes__icontains=search)
            )
        
        # Sorting
        sort_by = self.request.GET.get('sort', '-wo_date')
        sort_direction = self.request.GET.get('direction', 'desc')
        
        # Validate sort field
        allowed_sort_fields = {
            'wo_number': 'wo_number',
            'wo_date': 'wo_date',
            'job__business_name': 'job__business_name',
            'job__contact_name': 'job__contact_name',
            'job__status': 'job__status',
            'job__calendar__name': 'job__calendar__name',
            'created_at': 'created_at',
        }
        
        if sort_by in allowed_sort_fields:
            sort_field = allowed_sort_fields[sort_by]
            if sort_direction == 'desc':
                sort_field = f'-{sort_field}'
            queryset = queryset.order_by(sort_field)
        else:
            # Default sorting
            queryset = queryset.order_by('-wo_date')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Work Orders'
        context['calendars'] = Calendar.objects.filter(is_active=True)
        context['status_choices'] = Job.STATUS_CHOICES
        
        # Add sorting context
        context['current_sort'] = self.request.GET.get('sort', 'wo_date')
        context['current_direction'] = self.request.GET.get('direction', 'desc')
        
        # Add filter context for maintaining state
        context['current_filters'] = {
            'search': self.request.GET.get('search', ''),
            'status': self.request.GET.get('status', ''),
            'calendar': self.request.GET.get('calendar', ''),
        }
        
        return context


class WorkOrderDetailView(DetailView):
    """View work order details"""
    model = WorkOrder
    template_name = 'rental_scheduler/workorders/workorder_detail.html'
    context_object_name = 'work_order'
    
    def get_queryset(self):
        return WorkOrder.objects.select_related('job__calendar').prefetch_related('lines')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Work Order: {self.object.wo_number}'
        return context


class WorkOrderCreateView(CreateView):
    """Create a new work order"""
    model = WorkOrder
    form_class = WorkOrderForm
    template_name = 'rental_scheduler/workorders/workorder_form.html'
    success_url = reverse_lazy('rental_scheduler:workorder_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Work Order'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Work Order "{form.instance.wo_number}" created successfully.')
        return super().form_valid(form)


class WorkOrderUpdateView(UpdateView):
    """Update an existing work order"""
    model = WorkOrder
    form_class = WorkOrderForm
    template_name = 'rental_scheduler/workorders/workorder_form.html'
    success_url = reverse_lazy('rental_scheduler:workorder_list')
    
    def get_queryset(self):
        return WorkOrder.objects.select_related('job__calendar')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Update Work Order: {self.object.wo_number}'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Work Order "{form.instance.wo_number}" updated successfully.')
        return super().form_valid(form)


class WorkOrderDeleteView(DeleteView):
    """Delete a work order"""
    model = WorkOrder
    template_name = 'rental_scheduler/workorders/workorder_confirm_delete.html'
    success_url = reverse_lazy('rental_scheduler:workorder_list')
    
    def get_queryset(self):
        return WorkOrder.objects.select_related('job__calendar')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Delete Work Order: {self.object.wo_number}'
        return context
    
    def delete(self, request, *args, **kwargs):
        work_order = self.get_object()
        messages.success(request, f'Work Order "{work_order.wo_number}" deleted successfully.')
        return super().delete(request, *args, **kwargs)


class WorkOrderPrintView(DetailView):
    """Print work order view"""
    model = WorkOrder
    template_name = 'rental_scheduler/workorders/workorder_print.html'
    context_object_name = 'work_order'
    
    def get_queryset(self):
        return WorkOrder.objects.select_related('job__calendar').prefetch_related('lines')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Work Order'
        return context


class WorkOrderCustomerPrintView(DetailView):
    """Print customer copy work order view"""
    model = WorkOrder
    template_name = 'rental_scheduler/workorders/workorder_customer_print.html'
    context_object_name = 'work_order'
    
    def get_queryset(self):
        return WorkOrder.objects.select_related('job__calendar').prefetch_related('lines')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Customer Work Order'
        return context


# Invoice Views  
class InvoiceListView(ListView):
    """List all invoices"""
    model = Invoice
    template_name = 'rental_scheduler/invoices/invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 25
    
    def get_queryset(self):
        return Invoice.objects.select_related('job__calendar', 'work_order').filter(is_deleted=False)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Invoices'
        return context


class InvoiceDetailView(DetailView):
    """View invoice details"""
    model = Invoice
    template_name = 'rental_scheduler/invoices/invoice_detail.html'
    context_object_name = 'invoice'
    
    def get_queryset(self):
        return Invoice.objects.select_related('job__calendar', 'work_order').prefetch_related('lines')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Invoice: {self.object.invoice_number}'
        return context


# Job Modal Views
def job_create_partial(request):
    """Return job creation form partial for panel"""
    call_reminder_notes = ''
    
    # Check if editing existing job
    if 'edit' in request.GET:
        try:
            job_id = int(request.GET['edit'])
            job = get_object_or_404(Job, pk=job_id)
            form = JobForm(instance=job)
            
            # Load call reminder notes if job has a call reminder
            if job.has_call_reminder:
                from .models import CallReminder
                call_reminder = CallReminder.objects.filter(job=job).first()
                if call_reminder:
                    call_reminder_notes = call_reminder.notes or ''
        except (ValueError, TypeError):
            form = JobForm()
    else:
        # New job creation
        initial = {'all_day': True}
        if 'date' in request.GET:
            try:
                from datetime import datetime
                date_str = request.GET['date']
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                # Use date-only format since all_day is True by default
                initial['start_dt'] = date_obj.strftime(DATE_ONLY_FMT)
                initial['end_dt'] = date_obj.strftime(DATE_ONLY_FMT)
            except ValueError:
                pass  # Invalid date format, ignore
        else:
            # No date provided - default to today
            from datetime import date as _date
            today = _date.today()
            # Use date-only format since all_day is True by default
            initial['start_dt'] = today.strftime(DATE_ONLY_FMT)
            initial['end_dt'] = today.strftime(DATE_ONLY_FMT)
        
        # Pre-select calendar based on current filter
        if 'calendar' in request.GET:
            try:
                calendar_id = int(request.GET['calendar'])
                calendar = Calendar.objects.filter(pk=calendar_id, is_active=True).first()
                if calendar:
                    initial['calendar'] = calendar
            except (ValueError, TypeError):
                pass  # Invalid calendar ID, ignore
        
        form = JobForm(initial=initial)
    
    return render(request, 'rental_scheduler/jobs/_job_form_partial.html', {
        'form': form,
        'call_reminder_notes': call_reminder_notes
    })


def job_detail_partial(request, pk):
    """Return job details partial for panel"""
    job = get_object_or_404(Job, pk=pk)
    return render(request, 'rental_scheduler/jobs/_job_detail_partial.html', {'job': job})


@require_http_methods(["POST"])
def job_create_submit(request):
    """Handle job creation/update form submission"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("="*80)
    logger.info(f"job_create_submit called with POST data: {dict(request.POST)}")
    logger.info(f"all_day value: {request.POST.get('all_day')}")
    logger.info(f"start_dt value: {request.POST.get('start_dt')}")
    logger.info(f"end_dt value: {request.POST.get('end_dt')}")
    logger.info("="*80)
    
    # Check if this is an update (job ID in form data)
    job_id = request.POST.get('job_id')
    if job_id:
        try:
            job = get_object_or_404(Job, pk=job_id)
            form = JobForm(request.POST, instance=job)
            logger.info(f"Updating existing job {job_id}")
        except (ValueError, TypeError):
            form = JobForm(request.POST)
            logger.info("Creating new job (invalid job_id)")
    else:
        form = JobForm(request.POST)
        logger.info("Creating new job")
    
    logger.info(f"Form is_valid: {form.is_valid()}")
    if not form.is_valid():
        logger.error(f"Form validation FAILED!")
        logger.error(f"Form errors: {form.errors}")
        logger.error(f"Form errors as dict: {dict(form.errors)}")
        for field, errors in form.errors.items():
            logger.error(f"  Field '{field}': {errors}")
    
    if form.is_valid():
        job = form.save(commit=False)
        
        # Explicitly handle checkbox fields (unchecked checkboxes don't send data)
        has_call_reminder = request.POST.get('has_call_reminder') == 'on'
        call_reminder_weeks = request.POST.get('call_reminder_weeks_prior')
        call_reminder_completed = request.POST.get('call_reminder_completed') == 'on'
        
        logger.info(f"Call reminder checkbox: {has_call_reminder}, weeks: {call_reminder_weeks}, completed: {call_reminder_completed}")
        
        job.has_call_reminder = has_call_reminder
        job.call_reminder_completed = call_reminder_completed
        if job.has_call_reminder and call_reminder_weeks:
            try:
                job.call_reminder_weeks_prior = int(call_reminder_weeks)
            except (ValueError, TypeError):
                job.call_reminder_weeks_prior = None
        else:
            job.call_reminder_weeks_prior = None
        
        job.save()
        
        # Handle call reminder notes - save to CallReminder object
        call_reminder_notes = request.POST.get('call_reminder_notes', '').strip()
        if job.has_call_reminder and job.call_reminder_weeks_prior:
            from .models import CallReminder
            from .utils.events import get_call_reminder_sunday
            
            # Calculate reminder date
            reminder_date = get_call_reminder_sunday(job.start_dt, job.call_reminder_weeks_prior).date()
            
            # Get or create CallReminder for this job
            call_reminder, created = CallReminder.objects.get_or_create(
                job=job,
                calendar=job.calendar,
                defaults={'reminder_date': reminder_date, 'notes': call_reminder_notes}
            )
            
            # Update if it already exists
            if not created:
                call_reminder.reminder_date = reminder_date
                call_reminder.notes = call_reminder_notes
                call_reminder.completed = job.call_reminder_completed
                call_reminder.save()
        
        # Handle recurring event creation
        recurrence_enabled = request.POST.get('recurrence_enabled') == 'on'
        if recurrence_enabled and not job_id:  # Only on creation, not updates
            # Don't allow instances to become recurring parents
            if job.recurrence_parent:
                messages.error(request, 'Cannot make a recurring instance into a new recurring series. Edit the parent series instead.')
                return redirect('rental_scheduler:job_list')
            
            recurrence_type = request.POST.get('recurrence_type', 'monthly')
            recurrence_interval = int(request.POST.get('recurrence_interval', 1))
            recurrence_count = request.POST.get('recurrence_count')
            recurrence_until = request.POST.get('recurrence_until')
            
            # Convert count to int if provided and validate
            count = int(recurrence_count) if recurrence_count else None
            if count and count > 500:
                messages.error(request, 'Recurrence count cannot exceed 500 occurrences.')
                return redirect('rental_scheduler:job_list')
            until_date = recurrence_until if recurrence_until else None
            
            # Create recurrence rule
            job.create_recurrence_rule(
                recurrence_type=recurrence_type,
                interval=recurrence_interval,
                count=count,
                until_date=until_date
            )
            
            # Generate recurring instances
            job.generate_recurring_instances()
            logger.info(f"Created recurring job {job.id} with {recurrence_type} recurrence")
        
        logger.info(f"Job saved successfully: {job.id}")
        # Return a simple success response that triggers the close action
        # Include job ID in the trigger for the minimize button to use
        import json as json_module
        trigger_data = json_module.dumps({'jobSaved': {'jobId': job.id}})
        return HttpResponse(
            f'<input type="hidden" name="job_id" value="{job.id}" hx-swap-oob="true"><div hx-swap-oob="true" id="job-success">Job saved successfully!</div>', 
            headers={'HX-Trigger': trigger_data}
        )
    else:
        logger.error(f"Form validation errors: {form.errors}")
        return render(request, 'rental_scheduler/jobs/_job_form_partial.html', {'form': form}, status=400)

# API Views for Job Updates
@require_http_methods(["POST"])
@csrf_protect
def job_create_api(request):
    """API endpoint to create a new job"""
    try:
        # Parse JSON data
        data = json.loads(request.body)
        print(f"DEBUG: Received data: {data}")  # Debug logging
        
        # Create new job
        job = Job()
        
        # Set job fields
        job.business_name = data.get('business_name', '')
        job.contact_name = data.get('contact_name', '')
        job.phone = data.get('phone', '')
        job.trailer_color = data.get('trailer_color', '')
        job.trailer_serial = data.get('trailer_serial', '')
        job.trailer_details = data.get('trailer_details', '')
        job.notes = data.get('notes', '')
        job.repair_notes = data.get('repair_notes', '')
        job.status = data.get('status', 'uncompleted')
        
        # Handle repeat settings
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
        
        # Handle dates with normalization for all-day events
        start_value = data.get('start', data.get('start_dt'))
        end_value = data.get('end', data.get('end_dt'))
        
        if start_value:
            try:
                # Use normalization helper for proper timezone handling
                start_dt_utc, end_dt_utc, _, _, _ = normalize_event_datetimes(
                    start_value,
                    end_value,
                    job.all_day
                )
                job.start_dt = start_dt_utc
                job.end_dt = end_dt_utc
            except (ValueError, TypeError) as e:
                return JsonResponse({'error': f'Invalid date format: {str(e)}'}, status=400)
        
        # Set default calendar to first active calendar
        first_calendar = Calendar.objects.filter(is_active=True).first()
        if first_calendar:
            job.calendar = first_calendar
        
        # Save the job
        print(f"DEBUG: About to save job with start_dt={job.start_dt}, end_dt={job.end_dt}")  # Debug logging
        job.save()
        print(f"DEBUG: Job saved successfully with ID: {job.id}")  # Debug logging
        
        # Return created job data with proper formatting for FullCalendar
        if job.all_day:
            start_str = timezone.localtime(job.start_dt).date().isoformat()
            end_str = timezone.localtime(job.end_dt).date().isoformat()
        else:
            # Use strftime to avoid timezone offset in ISO string
            start_str = timezone.localtime(job.start_dt).strftime('%Y-%m-%dT%H:%M:%S')
            end_str = timezone.localtime(job.end_dt).strftime('%Y-%m-%dT%H:%M:%S')
        
        return JsonResponse({
            'id': job.id,
            'business_name': job.business_name,
            'contact_name': job.contact_name,
            'phone': job.phone,
            'trailer_color': job.trailer_color,
            'trailer_serial': job.trailer_serial,
            'trailer_details': job.trailer_details,
            'start': start_str,
            'end': end_str,
            'allDay': job.all_day,
            'status': job.status,
            'notes': job.notes,
            'repair_notes': job.repair_notes,
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"DEBUG: Error creating job: {e}")  # Debug logging
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_protect
def job_update_api(request, pk):
    """API endpoint for updating job data with CSRF protection"""
    
    try:
        job = get_object_or_404(Job, pk=pk)
        
        # Parse JSON data
        data = json.loads(request.body)
        
        # Update job fields
        job.business_name = data.get('business_name', job.business_name)
        job.contact_name = data.get('contact_name', job.contact_name)
        job.phone = data.get('phone', job.phone)
        job.trailer_color = data.get('trailer_color', job.trailer_color)
        job.trailer_serial = data.get('trailer_serial', job.trailer_serial)
        job.trailer_details = data.get('trailer_details', job.trailer_details)
        job.notes = data.get('notes', job.notes)
        job.repair_notes = data.get('repair_notes', job.repair_notes)
        job.status = data.get('status', job.status)
        
        # Handle repeat settings
        if 'repeat_type' in data:
            job.repeat_type = data.get('repeat_type', 'none') or 'none'
            if job.repeat_type == 'monthly':
                job.repeat_n_months = int(data.get('repeat_n_months', data.get('repeat_months', 1)))
            else:
                job.repeat_n_months = None
        
        # Determine if this is an all-day event
        if 'allDay' in data or 'all_day' in data:
            all_day = data.get('allDay', data.get('all_day', job.all_day))
            if isinstance(all_day, str):
                all_day = all_day.lower() in ('true', '1', 'yes', 'on')
            job.all_day = bool(all_day)
        
        # Handle dates with normalization for all-day events
        start_value = data.get('start', data.get('start_dt'))
        end_value = data.get('end', data.get('end_dt'))
        
        if start_value or end_value:
            # Use current values as fallback if one is missing
            if not start_value:
                start_value = job.start_dt
            if not end_value:
                end_value = job.end_dt
            
            try:
                # Use normalization helper for proper timezone handling
                start_dt_utc, end_dt_utc, _, _, _ = normalize_event_datetimes(
                    start_value,
                    end_value,
                    job.all_day
                )
                job.start_dt = start_dt_utc
                job.end_dt = end_dt_utc
            except (ValueError, TypeError) as e:
                return JsonResponse({'error': f'Invalid date format: {str(e)}'}, status=400)
        
        # Save the job
        job.save()
        
        # Return updated job data with proper formatting for FullCalendar
        if job.all_day:
            start_str = timezone.localtime(job.start_dt).date().isoformat()
            end_str = timezone.localtime(job.end_dt).date().isoformat()
        else:
            # Use strftime to avoid timezone offset in ISO string
            start_str = timezone.localtime(job.start_dt).strftime('%Y-%m-%dT%H:%M:%S')
            end_str = timezone.localtime(job.end_dt).strftime('%Y-%m-%dT%H:%M:%S')
        
        return JsonResponse({
            'id': job.id,
            'business_name': job.business_name,
            'contact_name': job.contact_name,
            'phone': job.phone,
            'trailer_color': job.trailer_color,
            'trailer_serial': job.trailer_serial,
            'trailer_details': job.trailer_details,
            'start': start_str,
            'end': end_str,
            'allDay': job.all_day,
            'status': job.status,
            'notes': job.notes,
            'repair_notes': job.repair_notes,
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def job_detail_api(request, pk):
    """API endpoint to get job details"""
    try:
        job = get_object_or_404(Job, pk=pk)
        
        # Return job data
        return JsonResponse({
            'id': job.id,
            'business_name': job.business_name,
            'contact_name': job.contact_name,
            'phone': job.phone,
            'trailer_color': job.trailer_color,
            'trailer_serial': job.trailer_serial,
            'trailer_details': job.trailer_details,
            'start_dt': job.start_dt.isoformat() if job.start_dt else None,
            'end_dt': job.end_dt.isoformat() if job.end_dt else None,
            'all_day': job.all_day,
            'status': job.status,
            'notes': job.notes,
            'repair_notes': job.repair_notes,
            'display_name': job.display_name,
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_protect
@require_http_methods(["POST"])
def workorder_add_line_api(request, pk):
    """API endpoint to add a line item to a work order"""
    try:
        # Get the work order
        work_order = get_object_or_404(WorkOrder, pk=pk)
        
        # Create form with the submitted data
        form = WorkOrderLineForm(request.POST)
        
        if form.is_valid():
            # Save the line item with the work order
            line_item = form.save(commit=False)
            line_item.work_order = work_order
            line_item.save()
            
            # Render the new line item HTML
            from django.template.loader import render_to_string
            line_html = render_to_string('rental_scheduler/partials/workorder_line_row.html', {
                'line': line_item
            })
            
            return JsonResponse({
                'status': 'success',
                'message': 'Line item added successfully',
                'line_html': line_html,
                'total_amount': str(work_order.total_amount)
            })
        else:
            return JsonResponse({
                'status': 'error',
                'error': 'Validation failed: ' + ', '.join([f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()])
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': f'Failed to add line item: {str(e)}'
        }, status=500)


def extract_phone_from_text(text):
    """
    Extract phone number from text using regex patterns.
    Handles formats like: 740-501-9004, 231-6407, (330) 265-4243, etc.
    """
    if not text:
        return None
    
    # Common phone patterns
    patterns = [
        r'\b\d{3}-\d{3}-\d{4}\b',  # 740-501-9004
        r'\b\d{3}-\d{4}\b',        # 231-6407
        r'\(\d{3}\)\s*\d{3}-\d{4}', # (330) 265-4243
        r'\b\d{3}\s+\d{3}-\d{4}\b', # 330 265-4243
        r'\b\d{10}\b',             # 7405019004
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    
    return None


def parse_ics_datetime(dt_value, is_all_day=False):
    """
    Convert iCalendar datetime to timezone-aware datetime.
    Handles both DATE and DATETIME formats.
    """
    if dt_value is None:
        return None
    
    # If it's already a datetime object
    if isinstance(dt_value, datetime):
        # Make it timezone-aware if it isn't
        if timezone.is_naive(dt_value):
            return timezone.make_aware(dt_value)
        return dt_value
    
    # If it's a date object (all-day event)
    if isinstance(dt_value, date):
        # Convert to datetime at midnight
        dt = datetime.combine(dt_value, datetime.min.time())
        return timezone.make_aware(dt)
    
    return None


def convert_rrule_to_json(rrule_str):
    """
    Convert iCalendar RRULE string to our JSON format.
    Example: "FREQ=YEARLY;UNTIL=20280128" -> {"type": "yearly", "interval": 1, "until_date": "2028-01-28"}
    """
    if not rrule_str:
        return None
    
    try:
        # Parse RRULE components
        parts = {}
        for part in rrule_str.split(';'):
            if '=' in part:
                key, value = part.split('=', 1)
                parts[key] = value
        
        # Extract frequency
        freq = parts.get('FREQ', '').lower()
        if freq not in ['yearly', 'monthly', 'weekly', 'daily']:
            return None
        
        # Build JSON rule
        rule = {
            'type': freq,
            'interval': int(parts.get('INTERVAL', 1))
        }
        
        # Add count if present
        if 'COUNT' in parts:
            rule['count'] = int(parts['COUNT'])
        
        # Add until date if present
        if 'UNTIL' in parts:
            until_str = parts['UNTIL']
            # Parse UNTIL date (format: YYYYMMDD or YYYYMMDDTHHMMSSZ)
            if 'T' in until_str:
                until_str = until_str.split('T')[0]
            # Format as YYYY-MM-DD
            if len(until_str) >= 8:
                rule['until_date'] = f"{until_str[:4]}-{until_str[4:6]}-{until_str[6:8]}"
        
        return rule
    
    except Exception as e:
        logger.error(f"Error parsing RRULE: {rrule_str}, Error: {str(e)}")
        return None


@csrf_protect
def calendar_import(request):
    """
    View for importing calendar events from .ics files.
    Displays upload form and processes imported events.
    """
    results = None
    
    logger.info(f"[DEBUG] calendar_import called - Method: {request.method}")
    
    if request.method == 'POST':
        logger.info(f"[DEBUG] POST data keys: {list(request.POST.keys())}")
        logger.info(f"[DEBUG] FILES data keys: {list(request.FILES.keys())}")
        logger.info(f"[DEBUG] Calendar value: {request.POST.get('calendar', 'NOT FOUND')}")
        logger.info(f"[DEBUG] File in FILES: {'ics_file' in request.FILES}")
        
        form = CalendarImportForm(request.POST, request.FILES)
        
        logger.info(f"[DEBUG] Form is_valid: {form.is_valid()}")
        if not form.is_valid():
            logger.error(f"[DEBUG] Form errors: {form.errors}")
            logger.error(f"[DEBUG] Form errors dict: {dict(form.errors)}")
        
        if form.is_valid():
            try:
                from icalendar import Calendar as ICalendar
                import uuid
                
                # Get the uploaded file and selected calendar
                ics_file = request.FILES['ics_file']
                target_calendar = form.cleaned_data['calendar']
                use_ai_parsing = form.cleaned_data.get('use_ai_parsing', True)
                
                # Generate unique batch ID for this import
                batch_id = str(uuid.uuid4())
                
                logger.info(f"Starting calendar import - AI parsing: {use_ai_parsing}")
                
                # Read and parse the .ics file
                ics_content = ics_file.read()
                cal = ICalendar.from_ical(ics_content)
                
                # Track results
                imported_count = 0
                skipped_count = 0
                error_count = 0
                errors = []
                
                # Process each event
                for component in cal.walk():
                    if component.name == "VEVENT":
                        try:
                            # Extract fields
                            summary = str(component.get('summary', ''))
                            description = str(component.get('description', ''))
                            dtstart = component.get('dtstart')
                            dtend = component.get('dtend')
                            created = component.get('created')
                            rrule = component.get('rrule')
                            status = component.get('status')
                            uid = str(component.get('uid', ''))
                            
                            # Determine job status - map CANCELLED to completed
                            job_status = 'uncompleted'  # Default
                            if status:
                                status_str = str(status).upper()
                                if status_str == 'CANCELLED':
                                    job_status = 'completed'
                            
                            # Skip if missing required fields
                            if not dtstart or not dtend:
                                skipped_count += 1
                                errors.append(f"Event '{summary}' skipped: missing start or end date")
                                continue
                            
                            # Get datetime values
                            dtstart_val = dtstart.dt if hasattr(dtstart, 'dt') else dtstart
                            dtend_val = dtend.dt if hasattr(dtend, 'dt') else dtend
                            
                            # Check if all-day event
                            is_all_day = isinstance(dtstart_val, date) and not isinstance(dtstart_val, datetime)
                            
                            # Parse dates
                            start_dt = parse_ics_datetime(dtstart_val, is_all_day)
                            end_dt = parse_ics_datetime(dtend_val, is_all_day)
                            
                            if not start_dt or not end_dt:
                                skipped_count += 1
                                errors.append(f"Event '{summary}' skipped: invalid date format")
                                continue
                            
                            # For all-day events, adjust end time
                            if is_all_day:
                                end_dt = end_dt.replace(hour=23, minute=59, second=59)
                            
                            # Extract phone from summary
                            phone = extract_phone_from_text(summary)
                            
                            # Remove phone from business_name if found
                            business_name = summary
                            if phone:
                                business_name = re.sub(r'\s*' + re.escape(phone) + r'\s*', ' ', business_name).strip()
                            
                            # Parse date_call_received
                            date_call_received = None
                            if created:
                                created_val = created.dt if hasattr(created, 'dt') else created
                                date_call_received = parse_ics_datetime(created_val)
                            
                            # Convert RRULE if present
                            recurrence_rule = None
                            if rrule:
                                rrule_str = str(rrule.to_ical().decode('utf-8'))
                                recurrence_rule = convert_rrule_to_json(rrule_str)
                            
                            # Parse description with AI to extract structured fields (if enabled)
                            if use_ai_parsing:
                                parsed_description = parse_description_with_ai(description)
                            else:
                                # No AI parsing - use raw description in notes
                                parsed_description = {
                                    'trailer_color': '',
                                    'trailer_serial': '',
                                    'trailer_details': '',
                                    'repair_notes': '',
                                    'quote': None,
                                    'unparsed_notes': description
                                }
                            
                            # Create Job instance
                            job = Job(
                                calendar=target_calendar,
                                status=job_status,
                                business_name=business_name[:150] if business_name else '',  # Limit to field max_length
                                phone=phone[:25] if phone else '',
                                start_dt=start_dt,
                                end_dt=end_dt,
                                all_day=is_all_day,
                                notes=parsed_description.get('unparsed_notes', description),
                                repair_notes=parsed_description.get('repair_notes', ''),
                                trailer_color=parsed_description.get('trailer_color', '')[:60],  # Limit to field max_length
                                trailer_serial=parsed_description.get('trailer_serial', '')[:120],  # Limit to field max_length
                                trailer_details=parsed_description.get('trailer_details', '')[:200],  # Limit to field max_length
                                quote=parsed_description.get('quote'),
                                date_call_received=date_call_received,
                                recurrence_rule=recurrence_rule,
                                import_batch_id=batch_id,  # Track import batch
                                created_by=request.user if request.user.is_authenticated else None,
                            )
                            
                            # Validate and save
                            job.full_clean()
                            job.save()
                            
                            imported_count += 1
                            
                        except Exception as e:
                            error_count += 1
                            event_name = summary if 'summary' in locals() else 'Unknown'
                            error_msg = f"Event '{event_name}' error: {str(e)}"
                            errors.append(error_msg)
                            logger.error(f"Import error for UID {uid}: {str(e)}")
                
                # Prepare results
                results = {
                    'success': True,
                    'imported': imported_count,
                    'skipped': skipped_count,
                    'errors_count': error_count,
                    'error_details': errors[:20],  # Show first 20 errors
                    'calendar_name': target_calendar.name
                }
                
                # Debug logging
                logger.info(f"Import complete: {imported_count} imported, {skipped_count} skipped, {error_count} errors")
                
                # Create comprehensive success message
                message_parts = []
                message_parts.append(f'✓ Import Complete: {imported_count} event(s) successfully imported to "{target_calendar.name}"')
                
                if skipped_count > 0:
                    message_parts.append(f'{skipped_count} skipped')
                if error_count > 0:
                    message_parts.append(f'{error_count} had errors')
                
                messages.success(request, ' | '.join(message_parts))
                
                # Redirect to calendar to see imported events
                return redirect('rental_scheduler:calendar')
                
            except Exception as e:
                messages.error(request, f'Failed to import calendar: {str(e)}')
                logger.error(f"Calendar import error: {str(e)}")
                # Keep the form with data so user can see what they selected
                # form already has the POST data from line 1370
        else:
            # Form validation failed - show errors to user
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CalendarImportForm()
    
    return render(request, 'rental_scheduler/jobs/job_import.html', {
        'form': form,
        'title': 'Import Calendar Events'
    })


def import_history(request):
    """
    View showing recent calendar imports with ability to revert them.
    """
    from django.db.models import Count, Min, Max
    
    # Get all import batches with aggregated info
    imports = (Job.objects
               .filter(import_batch_id__isnull=False)
               .values('import_batch_id', 'calendar__name', 'calendar__id')
               .annotate(
                   count=Count('id'),
                   first_date=Min('start_dt'),
                   last_date=Max('start_dt'),
                   imported_at=Min('created_at')
               )
               .order_by('-imported_at'))
    
    return render(request, 'rental_scheduler/jobs/import_history.html', {
        'imports': imports,
        'title': 'Import History'
    })


@csrf_protect
@require_http_methods(["POST"])
def revert_import(request, batch_id):
    """
    Delete all jobs from a specific import batch.
    """
    try:
        # Get all jobs in this batch
        jobs = Job.objects.filter(import_batch_id=batch_id)
        count = jobs.count()
        
        if count == 0:
            messages.warning(request, 'No jobs found for this import batch.')
            return redirect('rental_scheduler:import_history')
        
        # Delete all jobs in the batch
        jobs.delete()
        
        messages.success(request, f'Successfully reverted import: {count} job(s) deleted.')
        logger.info(f"Reverted import batch {batch_id}: {count} jobs deleted")
        
    except Exception as e:
        messages.error(request, f'Failed to revert import: {str(e)}')
        logger.error(f"Error reverting import {batch_id}: {str(e)}")
    
    return redirect('rental_scheduler:import_history')


# JSON Export/Import Views
@require_http_methods(["GET"])
def export_jobs(request, calendar_id=None):
    """
    Export jobs to JSON format for importing into another instance.
    Optionally filter by calendar_id.
    """
    try:
        # Get jobs to export
        jobs_qs = Job.objects.filter(is_deleted=False).select_related('calendar')
        
        export_source = "all"
        if calendar_id:
            calendar = get_object_or_404(Calendar, pk=calendar_id)
            jobs_qs = jobs_qs.filter(calendar=calendar)
            export_source = calendar.name
        
        # Order by start_dt for consistent export
        jobs_qs = jobs_qs.order_by('start_dt')
        
        # Build export data
        jobs_data = []
        parent_id_map = {}  # Map old parent IDs to temporary IDs for import
        
        for idx, job in enumerate(jobs_qs):
            job_dict = {
                # Basic info
                'business_name': job.business_name,
                'contact_name': job.contact_name,
                'phone': job.phone,
                
                # Address
                'address_line1': job.address_line1,
                'address_line2': job.address_line2,
                'city': job.city,
                'state': job.state,
                'postal_code': job.postal_code,
                
                # Timing
                'date_call_received': job.date_call_received.isoformat() if job.date_call_received else None,
                'start_dt': job.start_dt.isoformat(),
                'end_dt': job.end_dt.isoformat(),
                'all_day': job.all_day,
                
                # Call reminder
                'has_call_reminder': job.has_call_reminder,
                'call_reminder_weeks_prior': job.call_reminder_weeks_prior,
                'call_reminder_completed': job.call_reminder_completed,
                
                # Legacy repeat
                'repeat_type': job.repeat_type,
                'repeat_n_months': job.repeat_n_months,
                
                # Recurring events
                'recurrence_rule': job.recurrence_rule,
                'recurrence_original_start': job.recurrence_original_start.isoformat() if job.recurrence_original_start else None,
                'end_recurrence_date': job.end_recurrence_date.isoformat() if job.end_recurrence_date else None,
                
                # Job details
                'notes': job.notes,
                'repair_notes': job.repair_notes,
                
                # Trailer info
                'trailer_color': job.trailer_color,
                'trailer_serial': job.trailer_serial,
                'trailer_details': job.trailer_details,
                
                # Quote
                'quote': str(job.quote) if job.quote else None,
                'trailer_color_overwrite': job.trailer_color_overwrite,
                'quote_text': job.quote_text,
                
                # Status
                'status': job.status,
            }
            
            # Handle recurring parent relationships
            if job.is_recurring_parent:
                job_dict['_is_recurring_parent'] = True
                job_dict['_temp_id'] = f"parent_{idx}"
                parent_id_map[job.id] = f"parent_{idx}"
            elif job.is_recurring_instance and job.recurrence_parent_id:
                job_dict['_is_recurring_instance'] = True
                # Will be resolved during import
                if job.recurrence_parent_id in parent_id_map:
                    job_dict['_parent_temp_id'] = parent_id_map[job.recurrence_parent_id]
            
            jobs_data.append(job_dict)
        
        # Build the export structure
        export_data = {
            'version': '1.0',
            'exported_at': timezone.now().isoformat(),
            'export_source': export_source,
            'job_count': len(jobs_data),
            'jobs': jobs_data
        }
        
        # Generate filename
        timestamp = timezone.now().strftime('%Y-%m-%d_%H%M%S')
        if calendar_id:
            filename = f"jobs_export_{export_source}_{timestamp}.json"
        else:
            filename = f"jobs_export_all_{timestamp}.json"
        
        # Create response
        response = HttpResponse(
            json.dumps(export_data, indent=2, ensure_ascii=False),
            content_type='application/json'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        logger.info(f"Exported {len(jobs_data)} jobs from '{export_source}'")
        return response
        
    except Exception as e:
        logger.error(f"Error exporting jobs: {str(e)}", exc_info=True)
        messages.error(request, f"Error exporting jobs: {str(e)}")
        return redirect('rental_scheduler:job_list')


@csrf_protect
def import_jobs_json(request):
    """
    Import jobs from JSON export file.
    Allows user to select target calendar for all imported jobs.
    """
    from .forms import JobImportForm
    
    if request.method == 'POST':
        form = JobImportForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                json_file = form.cleaned_data['json_file']
                target_calendar = form.cleaned_data['target_calendar']
                
                # Read and parse JSON
                json_file.seek(0)
                content = json_file.read()
                data = json.loads(content)
                
                # Validate version
                if data.get('version') != '1.0':
                    messages.warning(request, f"Warning: Export version {data.get('version')} may not be fully compatible.")
                
                jobs_data = data.get('jobs', [])
                if not jobs_data:
                    messages.warning(request, "No jobs found in the export file.")
                    return redirect('rental_scheduler:calendar_import')
                
                # Generate import batch ID for tracking
                import uuid
                batch_id = str(uuid.uuid4())
                
                # Import jobs within transaction
                with transaction.atomic():
                    imported_count = 0
                    parent_map = {}  # Map temp IDs to new parent Job instances
                    jobs_to_link = []  # Store (job, parent_temp_id) tuples for second pass
                    
                    # First pass: import all jobs
                    for job_data in jobs_data:
                        is_parent = job_data.pop('_is_recurring_parent', False)
                        is_instance = job_data.pop('_is_recurring_instance', False)
                        temp_id = job_data.pop('_temp_id', None)
                        parent_temp_id = job_data.pop('_parent_temp_id', None)
                        
                        # Parse datetime fields
                        if job_data.get('date_call_received'):
                            job_data['date_call_received'] = datetime.fromisoformat(job_data['date_call_received'])
                        if job_data.get('start_dt'):
                            job_data['start_dt'] = datetime.fromisoformat(job_data['start_dt'])
                        if job_data.get('end_dt'):
                            job_data['end_dt'] = datetime.fromisoformat(job_data['end_dt'])
                        if job_data.get('recurrence_original_start'):
                            job_data['recurrence_original_start'] = datetime.fromisoformat(job_data['recurrence_original_start'])
                        if job_data.get('end_recurrence_date'):
                            job_data['end_recurrence_date'] = date.fromisoformat(job_data['end_recurrence_date'])
                        
                        # Quote is now a CharField, keep as string
                        if job_data.get('quote'):
                            job_data['quote'] = str(job_data['quote'])
                        
                        # Create the job
                        job = Job(
                            calendar=target_calendar,
                            import_batch_id=batch_id,
                            **job_data
                        )
                        
                        # Bypass full_clean during import to avoid validation issues
                        # Call the parent Model.save() directly instead of Job.save()
                        models.Model.save(job, force_insert=True)
                        
                        imported_count += 1
                        
                        # Track parents for second pass
                        if is_parent and temp_id:
                            parent_map[temp_id] = job
                        elif is_instance and parent_temp_id:
                            # Store for second pass
                            jobs_to_link.append((job, parent_temp_id))
                    
                    # Second pass: link recurring instances to parents
                    for job, parent_temp_id in jobs_to_link:
                        if parent_temp_id in parent_map:
                            parent_job = parent_map[parent_temp_id]
                            job.recurrence_parent = parent_job
                            models.Model.save(job, update_fields=['recurrence_parent'])
                
                messages.success(
                    request,
                    f"Successfully imported {imported_count} job(s) into calendar '{target_calendar.name}'. "
                    f"Import batch ID: {batch_id[:8]}..."
                )
                logger.info(f"Imported {imported_count} jobs from JSON export into calendar '{target_calendar.name}' (batch: {batch_id})")
                
                return redirect('rental_scheduler:job_list')
                
            except json.JSONDecodeError as e:
                messages.error(request, f"Invalid JSON file: {str(e)}")
            except KeyError as e:
                messages.error(request, f"Missing required field in export data: {str(e)}")
            except Exception as e:
                logger.error(f"Error importing jobs from JSON: {str(e)}", exc_info=True)
                messages.error(request, f"Error importing jobs: {str(e)}")
    else:
        form = JobImportForm()
    
    context = {
        'title': 'Import Jobs from JSON',
        'form': form,
        'import_type': 'json'
    }
    
    return render(request, 'rental_scheduler/jobs/job_import_json.html', context)
