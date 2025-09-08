from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import UpdateView, TemplateView, ListView, CreateView, DeleteView, DetailView
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import Calendar, Job, WorkOrder, WorkOrderLine, Invoice, InvoiceLine, StatusChange
import os
from django.http import HttpResponse
import json
from django.db import models, transaction
from datetime import datetime
from decimal import Decimal
from django import forms
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
        context['calendars'] = Calendar.objects.filter(is_active=True)
        return context

# Calendar CRUD Views
class CalendarListView(ListView):
    """List all calendars with basic CRUD operations"""
    model = Calendar
    template_name = 'rental_scheduler/calendar_list.html'
    context_object_name = 'calendars'
    ordering = ['name']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Calendars'
        return context

class CalendarCreateView(CreateView):
    """Create a new calendar"""
    model = Calendar
    template_name = 'rental_scheduler/calendar_form.html'
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
    template_name = 'rental_scheduler/calendar_form.html'
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
    template_name = 'rental_scheduler/calendar_confirm_delete.html'
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
    template_name = 'rental_scheduler/job_list.html'
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
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none'
        }),
        input_formats=['%Y-%m-%dT%H:%M'],
        required=True,
        help_text="Start date and time of the job"
    )
    
    end_dt = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none'
        }),
        input_formats=['%Y-%m-%dT%H:%M'],
        required=True,
        help_text="End date and time of the job"
    )
    
    date_call_received = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none'
        }),
        input_formats=['%Y-%m-%dT%H:%M'],
        required=False,
        help_text="Date and time the initial call was received"
    )
    
    # Override the calendar field to make it visible
    calendar = forms.ModelChoiceField(
        queryset=Calendar.objects.filter(is_active=True),
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:border-gray-400 focus:outline-none'
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
            'start_dt', 'end_dt', 'all_day', 'repeat_type', 'notes',
            'trailer_color', 'trailer_serial', 'trailer_details', 'repair_notes', 'quote',
            'calendar', 'status'
        ]
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none'}),
            'contact_name': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none'}),
            'phone': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none'}),
            'all_day': forms.CheckboxInput(attrs={'class': 'h-4 w-4 rounded border-gray-300 mr-2'}),
            'repeat_type': forms.Select(attrs={'class': 'w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:border-gray-400 focus:outline-none'}),
            'notes': forms.Textarea(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none h-20 resize-none', 'rows': 3}),
            'trailer_color': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none'}),
            'trailer_serial': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none'}),
            'trailer_details': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none'}),
            'repair_notes': forms.Textarea(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none h-32 resize-none', 'rows': 5}),
            'quote': forms.NumberInput(attrs={'class': 'w-full rounded-md border border-gray-300 pl-7 pr-3 py-2 text-sm focus:border-gray-400 focus:outline-none', 'step': '0.01', 'min': '0'}),
        }


class JobCreateView(CreateView):
    """Create a new job"""
    model = Job
    form_class = JobForm
    template_name = 'rental_scheduler/job_form.html'
    success_url = reverse_lazy('rental_scheduler:job_list')
    
    def get_initial(self):
        """Set initial values for form fields"""
        initial = super().get_initial()
        
        # Set default calendar to first active calendar
        first_calendar = Calendar.objects.filter(is_active=True).first()
        if first_calendar:
            initial['calendar'] = first_calendar
        
        # Set default status
        initial['status'] = 'uncompleted'
        
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Job'
        context['calendars'] = Calendar.objects.filter(is_active=True)
        context['is_create'] = True
        return context
    
    def form_valid(self, form):
        """Process form submission and create job"""
        try:
            # Set the user who created this job
            if self.request.user.is_authenticated:
                form.instance.created_by = self.request.user
            
            # No need for customer/trailer auto-creation anymore
            # All info is stored directly in the job fields
            
            response = super().form_valid(form)
            messages.success(self.request, f'Job for {form.instance.get_display_name()} created successfully.')
            
            return response
            
        except Exception as e:
            logger.error(f"Error creating job: {str(e)}")
            messages.error(self.request, f"Error creating job: {str(e)}")
            return self.form_invalid(form)


class JobUpdateView(UpdateView):
    """Update an existing job"""
    model = Job
    form_class = JobForm
    template_name = 'rental_scheduler/job_form.html'
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
    template_name = 'rental_scheduler/job_detail.html'
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
    template_name = 'rental_scheduler/job_confirm_delete.html'
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
    template_name = 'rental_scheduler/job_print_wo.html'
    context_object_name = 'job'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Work Order'
        return context


class JobPrintWOCustomerView(DetailView):
    """Print customer copy work order view"""
    model = Job
    template_name = 'rental_scheduler/job_print_wo_customer.html'
    context_object_name = 'job'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Customer Work Order'
        return context


class JobPrintInvoiceView(DetailView):
    """Print invoice view"""
    model = Job
    template_name = 'rental_scheduler/job_print_invoice.html'
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
        
        # Build queryset
        jobs = Job.objects.select_related('calendar').filter(is_deleted=False)
        
        if start_date and end_date:
            jobs = jobs.filter(
                start_dt__lte=end_date,
                end_dt__gte=start_date
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
                'title': f"{job.trailer_color or 'Unknown'} Trailer - {display_name}{phone_display}",
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
        
        return JsonResponse(events, safe=False)
        
    except Exception as e:
        logger.error(f"Error getting calendar data: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
def update_job_status(request, job_id):
    """API endpoint to update job status"""
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
    """List all work orders"""
    model = WorkOrder
    template_name = 'rental_scheduler/workorder_list.html'
    context_object_name = 'work_orders'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = WorkOrder.objects.select_related('job__calendar')
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                models.Q(wo_number__icontains=search_query) |
                models.Q(job__business_name__icontains=search_query) |
                models.Q(job__contact_name__icontains=search_query) |
                models.Q(notes__icontains=search_query)
            )
        
        return queryset.order_by('-wo_date', '-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Work Orders'
        context['search_query'] = self.request.GET.get('search', '')
        return context


class WorkOrderDetailView(DetailView):
    """View work order details"""
    model = WorkOrder
    template_name = 'rental_scheduler/workorder_detail.html'
    context_object_name = 'work_order'
    
    def get_queryset(self):
        return WorkOrder.objects.select_related('job__calendar').prefetch_related('lines')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Work Order: {self.object.wo_number}'
        return context


# Invoice Views  
class InvoiceListView(ListView):
    """List all invoices"""
    model = Invoice
    template_name = 'rental_scheduler/invoice_list.html'
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
    template_name = 'rental_scheduler/invoice_detail.html'
    context_object_name = 'invoice'
    
    def get_queryset(self):
        return Invoice.objects.select_related('job__calendar', 'work_order').prefetch_related('lines')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Invoice: {self.object.invoice_number}'
        return context
