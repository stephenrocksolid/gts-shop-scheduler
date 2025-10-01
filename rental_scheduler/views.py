from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import UpdateView, TemplateView, ListView, CreateView, DeleteView, DetailView
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from .models import Calendar, Job, WorkOrder, WorkOrderLine, Invoice, InvoiceLine, StatusChange
from .forms import JobForm, WorkOrderForm, WorkOrderLineForm
import os
from django.http import HttpResponse
import json
from django.db import models, transaction
from datetime import datetime
from decimal import Decimal
from django import forms

# HTML5 datetime-local format constant
DATETIME_LOCAL_FMT = "%Y-%m-%dT%H:%M"
import logging
from django.template.loader import render_to_string
from rental_scheduler.utils.datetime import format_local, to_local

logger = logging.getLogger(__name__)

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
        import json
        context['calendars_json'] = json.dumps(context['calendars'])
        
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
    fields = ['name', 'color', 'is_active']
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
    fields = ['name', 'color', 'is_active']
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
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by calendar
        calendar_id = self.request.GET.get('calendar')
        if calendar_id:
            queryset = queryset.filter(calendar_id=calendar_id)
        
        # Search across multiple fields
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(business_name__icontains=search) |
                models.Q(contact_name__icontains=search) |
                models.Q(phone__icontains=search) |
                models.Q(address_line1__icontains=search) |
                models.Q(city__icontains=search) |
                models.Q(trailer_color__icontains=search) |
                models.Q(trailer_serial__icontains=search) |
                models.Q(trailer_details__icontains=search) |
                models.Q(repair_notes__icontains=search) |
                models.Q(quote_text__icontains=search)
            )
        
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
        context['calendars'] = Calendar.objects.filter(is_active=True)
        context['status_choices'] = Job.STATUS_CHOICES
        
        # Add sorting context
        context['current_sort'] = self.request.GET.get('sort', 'start_dt')
        context['current_direction'] = self.request.GET.get('direction', 'desc')
        
        # Add filter context for maintaining state
        context['current_filters'] = {
            'search': self.request.GET.get('search', ''),
            'status': self.request.GET.get('status', ''),
            'calendar': self.request.GET.get('calendar', ''),
        }
        
        return context


class JobForm(forms.ModelForm):
    """Custom form for Job creation with proper datetime handling"""
    
    # Override datetime fields to use proper widgets
    start_dt = forms.DateTimeField(
        required=True,
        input_formats=[DATETIME_LOCAL_FMT],
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none',
            'required': True
        }, format=DATETIME_LOCAL_FMT),
        help_text="Start date and time of the job"
    )
    
    end_dt = forms.DateTimeField(
        required=True,
        input_formats=[DATETIME_LOCAL_FMT],
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none',
            'required': True
        }, format=DATETIME_LOCAL_FMT),
        help_text="End date and time of the job"
    )
    
    date_call_received = forms.DateTimeField(
        required=False,
        input_formats=[DATETIME_LOCAL_FMT],
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
            'quote': forms.NumberInput(attrs={'class': 'w-full rounded-md border border-gray-300 pl-7 pr-3 py-2 text-sm focus:border-gray-400 focus:outline-none', 'step': '0.01', 'min': '0'}),
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
            # Normalize to day bounds (exclusive end - next day at midnight)
            start_normalized = datetime.combine(start_dt.date(), time.min)
            end_normalized = datetime.combine(end_dt.date(), time.min) + timedelta(days=1)
            
            # Make timezone-aware if using timezone support
            from django.utils import timezone
            if timezone.is_aware(start_dt):
                start_normalized = timezone.make_aware(start_normalized)
                end_normalized = timezone.make_aware(end_normalized)
            
            cleaned_data['start_dt'] = start_normalized
            cleaned_data['end_dt'] = end_normalized
        else:
            # Keep times as provided, just validate order
            if end_dt <= start_dt:
                self.add_error("end_dt", "End date/time must be after start date/time.")
        
        return cleaned_data


def job_create(request):
    """Create a new job - function-based view for better form handling"""
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save()
            messages.success(request, "Job created successfully.")
            return redirect("rental_scheduler:job_detail", pk=job.pk)
        else:
            # TEMP debug – keep for now, remove later
            print("FORM ERRORS:", form.errors.as_json())
    else:
        # Set initial values for new form
        initial = {}
        
        # Set default calendar to first active calendar
        first_calendar = Calendar.objects.filter(is_active=True).first()
        if first_calendar:
            initial['calendar'] = first_calendar
        
        # Set default status
        initial['status'] = 'uncompleted'
        
        form = JobForm(initial=initial)

    context = {
        'form': form,
        'title': 'Create Job',
        'calendars': Calendar.objects.filter(is_active=True)
    }
    return render(request, "rental_scheduler/jobs/job_form.html", context)


class JobUpdateView(UpdateView):
    """Update an existing job"""
    model = Job
    form_class = JobForm
    template_name = 'rental_scheduler/jobs/job_form.html'
    success_url = reverse_lazy('rental_scheduler:job_list')
    
    def get_queryset(self):
        return Job.objects.select_related('calendar')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Job: {self.object.get_display_name()}'
        context['calendars'] = Calendar.objects.filter(is_active=True)
        context['is_create'] = False
        return context
    
    def form_valid(self, form):
        """Process form submission and update job"""
        try:
            # Set the user who updated this job
            if self.request.user.is_authenticated:
                form.instance.updated_by = self.request.user
            
            response = super().form_valid(form)
            messages.success(self.request, f'Job for {form.instance.get_display_name()} updated successfully.')
            
            return response
            
        except Exception as e:
            logger.error(f"Error updating job: {str(e)}")
            messages.error(self.request, f"Error updating job: {str(e)}")
            return self.form_invalid(form)


class JobDetailView(DetailView):
    """View job details"""
    model = Job
    template_name = 'rental_scheduler/jobs/job_detail_simple.html'
    context_object_name = 'job'
    
    def get_queryset(self):
        return Job.objects.select_related('calendar')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Job Details: {self.object.get_display_name()}'
        return context


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
class JobPrintWOView(DetailView):
    """Print work order view"""
    model = Job
    template_name = 'rental_scheduler/jobs/job_print_wo.html'
    context_object_name = 'job'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Work Order'
        return context


class JobPrintWOCustomerView(DetailView):
    """Print customer copy work order view"""
    model = Job
    template_name = 'rental_scheduler/jobs/job_print_wo_customer.html'
    context_object_name = 'job'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Customer Work Order'
        return context


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
    try:
        # Get date range from request
        start_date = request.GET.get('start')
        end_date = request.GET.get('end')
        
        # Get filter parameters
        status_filter = request.GET.get('status')
        calendar_filter = request.GET.get('calendar')
        search_filter = request.GET.get('search')
        
        # Build queryset
        jobs = Job.objects.select_related('calendar').filter(is_deleted=False)
        
        # Apply date range filter
        if start_date and end_date:
            jobs = jobs.filter(
                start_dt__lte=end_date,
                end_dt__gte=start_date
            )
        
        # Apply status filter
        if status_filter:
            jobs = jobs.filter(status=status_filter)
        
        # Apply calendar filter
        if calendar_filter:
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
            # Format phone number with dashes
            phone_formatted = ""
            if job.get_phone():
                phone_str = str(int(job.get_phone()))
                if len(phone_str) == 10:
                    phone_formatted = f"{phone_str[:3]}-{phone_str[3:6]}-{phone_str[6:]}"
                else:
                    phone_formatted = phone_str
            
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
            
            event = {
                'id': f"job-{job.id}",
                'title': title,
                'start': job.start_dt.astimezone().isoformat(),
                'end': job.end_dt.astimezone().isoformat(),
                'backgroundColor': calendar_color,
                'borderColor': calendar_color,
                'allDay': job.all_day,
                'extendedProps': {
                    'type': 'job',
                    'job_id': job.id,
                    'status': job.status,
                    'calendar_id': job.calendar.id,
                    'calendar_name': job.calendar.name,
                    'calendar_color': job.calendar.color,
                    'business_name': job.business_name,
                    'contact_name': job.contact_name,
                    'phone': job.get_phone(),
                    'trailer_color': job.trailer_color,
                    'trailer_serial': job.trailer_serial,
                    'trailer_details': job.trailer_details,
                    'notes': job.notes,
                    'repair_notes': job.repair_notes,
                }
            }
            
            # Debug: Log the event colors being set
            print(f"API: Setting colors for job-{job.id}: backgroundColor={calendar_color}, calendar={job.calendar.name}")
            
            events.append(event)
        
        # Debug: Log the number of events and first event
        print(f"API: Returning {len(events)} events")
        if events:
            print(f"API: First event: {events[0]}")
        
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
def job_detail_modal(request, pk):
    """Return the read-only job details modal partial"""
    job = get_object_or_404(Job, pk=pk)
    return render(request, "rental_scheduler/jobs/_job_modal_detail.html", {"job": job})


def job_edit_modal(request, pk):
    """Return the editable job modal partial or handle form submission"""
    job = get_object_or_404(Job, pk=pk)
    
    if request.method == "POST":
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            job = form.save()
            # Return the updated read-only modal with status 200
            return render(request, "rental_scheduler/jobs/_job_modal_detail.html", {"job": job})
        else:
            # Return the edit modal with errors and status 400 so HTMX swaps it and shows errors
            return render(request, "rental_scheduler/jobs/_job_modal_edit.html", {
                "job": job, 
                "form": form
            }, status=400)
    else:
        # GET request - show edit form
        form = JobForm(instance=job)
        return render(request, "rental_scheduler/jobs/_job_modal_edit.html", {
            "job": job, 
            "form": form
        })


def job_detail_panel(request, pk):
    """Return the read-only job details panel partial"""
    job = get_object_or_404(Job, pk=pk)
    return render(request, "rental_scheduler/jobs/_job_panel_detail.html", {"job": job})


def job_edit_panel(request, pk):
    """Return the editable job panel partial or handle form submission"""
    job = get_object_or_404(Job, pk=pk)
    
    if request.method == "POST":
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            job = form.save()
            # Return the updated read-only panel with status 200
            return render(request, "rental_scheduler/jobs/_job_panel_detail.html", {"job": job})
        else:
            # Return the edit panel with errors and status 400 so HTMX swaps it and shows errors
            return render(request, "rental_scheduler/jobs/_job_panel_edit.html", {
                "job": job, 
                "form": form
            }, status=400)
    else:
        # GET request - show edit form
        form = JobForm(instance=job)
        return render(request, "rental_scheduler/jobs/_job_panel_edit.html", {
            "job": job,
            "form": form
        })


def job_create_panel(request):
    """Return the job creation panel partial or handle form submission"""
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save()
            # Return success message and close panel
            return render(request, "rental_scheduler/jobs/_job_panel_detail.html", {"job": job})
        else:
            # Return the create panel with errors and status 400 so HTMX swaps it and shows errors
            return render(request, "rental_scheduler/jobs/_job_panel_create.html", {
                "form": form
            }, status=400)
    else:
        # GET request - show create form
        form = JobForm()
        
        # Pre-fill date if provided in query params
        if 'date' in request.GET:
            try:
                from datetime import datetime
                date_str = request.GET['date']
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                # Set initial values for the form
                form.fields['start_dt'].initial = date_obj.strftime('%Y-%m-%dT09:00')
                form.fields['end_dt'].initial = date_obj.strftime('%Y-%m-%dT17:00')
            except ValueError:
                pass  # Invalid date format, ignore
        
        return render(request, "rental_scheduler/jobs/_job_panel_create.html", {
            "form": form
        })


def job_create_partial(request):
    """Return job creation form partial for panel"""
    # Check if editing existing job
    if 'edit' in request.GET:
        try:
            job_id = int(request.GET['edit'])
            job = get_object_or_404(Job, pk=job_id)
            form = JobForm(instance=job)
        except (ValueError, TypeError):
            form = JobForm()
    else:
        # New job creation
        initial = {}
        if 'date' in request.GET:
            try:
                from datetime import datetime
                date_str = request.GET['date']
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                # Set initial values for the form
                initial['start_dt'] = date_obj.strftime('%Y-%m-%dT09:00')
                initial['end_dt'] = date_obj.strftime('%Y-%m-%dT17:00')
            except ValueError:
                pass  # Invalid date format, ignore
        
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
    
    return render(request, 'rental_scheduler/jobs/_job_form_partial.html', {'form': form})


def job_detail_partial(request, pk):
    """Return job details partial for panel"""
    job = get_object_or_404(Job, pk=pk)
    return render(request, 'rental_scheduler/jobs/_job_detail_partial.html', {'job': job})


@require_http_methods(["POST"])
def job_create_submit(request):
    """Handle job creation/update form submission"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"job_create_submit called with POST data: {request.POST}")
    
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
    
    if form.is_valid():
        job = form.save()
        logger.info(f"Job saved successfully: {job.id}")
        return render(request, 'rental_scheduler/jobs/_job_detail_partial.html', {'job': job})
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
        job.all_day = data.get('all_day') == 'on' or data.get('all_day') == True
        
        # Handle dates
        if data.get('start_dt'):
            from datetime import datetime
            from django.utils import timezone
            try:
                # Parse datetime-local format (YYYY-MM-DDTHH:MM) as naive datetime
                naive_dt = datetime.fromisoformat(data['start_dt'])
                # Make it timezone-aware in local timezone, then convert to UTC for storage
                local_dt = timezone.make_aware(naive_dt)
                job.start_dt = local_dt
            except ValueError:
                return JsonResponse({'error': 'Invalid start date format'}, status=400)
        if data.get('end_dt'):
            from datetime import datetime
            from django.utils import timezone
            try:
                # Parse datetime-local format (YYYY-MM-DDTHH:MM) as naive datetime
                naive_dt = datetime.fromisoformat(data['end_dt'])
                # Make it timezone-aware in local timezone, then convert to UTC for storage
                local_dt = timezone.make_aware(naive_dt)
                job.end_dt = local_dt
            except ValueError:
                return JsonResponse({'error': 'Invalid end date format'}, status=400)
        
        # Set default calendar to first active calendar
        first_calendar = Calendar.objects.filter(is_active=True).first()
        if first_calendar:
            job.calendar = first_calendar
        
        # Save the job
        print(f"DEBUG: About to save job with start_dt={job.start_dt}, end_dt={job.end_dt}")  # Debug logging
        job.save()
        print(f"DEBUG: Job saved successfully with ID: {job.id}")  # Debug logging
        
        # Return created job data
        return JsonResponse({
            'id': job.id,
            'business_name': job.business_name,
            'contact_name': job.contact_name,
            'phone': job.phone,
            'trailer_color': job.trailer_color,
            'trailer_serial': job.trailer_serial,
            'trailer_details': job.trailer_details,
            'start_dt': job.start_dt.astimezone().isoformat() if job.start_dt else None,
            'end_dt': job.end_dt.astimezone().isoformat() if job.end_dt else None,
            'all_day': job.all_day,
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
        job.all_day = data.get('all_day') == 'on' or data.get('all_day') == True
        
        # Handle dates
        if data.get('start_dt'):
            from datetime import datetime
            from django.utils import timezone
            try:
                # Parse datetime-local format (YYYY-MM-DDTHH:MM) as naive datetime
                naive_dt = datetime.fromisoformat(data['start_dt'])
                # Make it timezone-aware in local timezone, then convert to UTC for storage
                local_dt = timezone.make_aware(naive_dt)
                job.start_dt = local_dt
            except ValueError:
                return JsonResponse({'error': 'Invalid start date format'}, status=400)
        if data.get('end_dt'):
            from datetime import datetime
            from django.utils import timezone
            try:
                # Parse datetime-local format (YYYY-MM-DDTHH:MM) as naive datetime
                naive_dt = datetime.fromisoformat(data['end_dt'])
                # Make it timezone-aware in local timezone, then convert to UTC for storage
                local_dt = timezone.make_aware(naive_dt)
                job.end_dt = local_dt
            except ValueError:
                return JsonResponse({'error': 'Invalid end date format'}, status=400)
        
        # Save the job
        job.save()
        
        # Return updated job data
        return JsonResponse({
            'id': job.id,
            'business_name': job.business_name,
            'contact_name': job.contact_name,
            'phone': job.phone,
            'trailer_color': job.trailer_color,
            'trailer_serial': job.trailer_serial,
            'trailer_details': job.trailer_details,
            'start_dt': job.start_dt.astimezone().isoformat() if job.start_dt else None,
            'end_dt': job.end_dt.astimezone().isoformat() if job.end_dt else None,
            'all_day': job.all_day,
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
