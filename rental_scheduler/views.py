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
        """Custom validation to ensure end date is after start date"""
        cleaned_data = super().clean()
        start_dt = cleaned_data.get("start_dt")
        end_dt = cleaned_data.get("end_dt")
        
        if start_dt and end_dt and end_dt < start_dt:
            self.add_error("end_dt", "End date must be after start date.")
        
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
        
        STATUS_COLORS = {
            'uncompleted': '#F59E0B',  # Yellow
            'completed': '#059669',   # Green
        }
        
        for job in jobs:
            display_name = job.get_display_name()
            phone_display = f"\n📞 {job.get_phone()}" if job.get_phone() else ""
            
            event = {
                'id': f"job-{job.id}",
                'title': f"{job.trailer_details or 'Unknown'} Trailer - {display_name}{phone_display}",
                'start': job.start_dt.isoformat(),
                'end': job.end_dt.isoformat(),
                'backgroundColor': STATUS_COLORS.get(job.status, '#6B7280'),
                'borderColor': STATUS_COLORS.get(job.status, '#6B7280'),
                'allDay': job.all_day,
                'extendedProps': {
                    'type': 'job',
                    'status': job.status,
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
            events.append(event)
        
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
            try:
                # Parse datetime-local format (YYYY-MM-DDTHH:MM)
                job.start_dt = datetime.fromisoformat(data['start_dt'])
            except ValueError:
                return JsonResponse({'error': 'Invalid start date format'}, status=400)
        if data.get('end_dt'):
            from datetime import datetime
            try:
                # Parse datetime-local format (YYYY-MM-DDTHH:MM)
                job.end_dt = datetime.fromisoformat(data['end_dt'])
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
            'start_dt': job.start_dt.isoformat() if job.start_dt else None,
            'end_dt': job.end_dt.isoformat() if job.end_dt else None,
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
            job.start_dt = data['start_dt']
        if data.get('end_dt'):
            job.end_dt = data['end_dt']
        
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
            'start_dt': job.start_dt.isoformat() if job.start_dt else None,
            'end_dt': job.end_dt.isoformat() if job.end_dt else None,
            'all_day': job.all_day,
            'status': job.status,
            'notes': job.notes,
            'repair_notes': job.repair_notes,
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
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
