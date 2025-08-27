from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import UpdateView, TemplateView, ListView, CreateView, DeleteView, DetailView
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import SystemSettings, TrailerCategory, Trailer, Contract, Customer, TrailerService
import os
from django.http import HttpResponse
import json
from django.db import models, transaction
from datetime import datetime
from decimal import Decimal
from django import forms
import logging
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from django.conf import settings
from rental_scheduler.utils.network import validate_network_path as validate_network
from rental_scheduler.utils.network import connect_to_network_share
from rental_scheduler.services.availability import is_trailer_available
from rental_scheduler.services.returns import backfill_missing_returns
from rental_scheduler.utils.datetime import format_local, to_local

logger = logging.getLogger(__name__)

def find_existing_customer(name, phone=None):
    """
    Smart customer lookup to prevent duplicates.
    
    Rules:
    - If phone exists: match by name + phone (case-insensitive)
    - If no phone: match by name only where phone is empty/null
    
    Returns existing Customer or None if no match found.
    """
    if not name or not name.strip():
        return None
        
    name = name.strip()
    
    if phone and phone.strip():
        # Match by name + phone (both must match exactly)
        return Customer.objects.filter(
            name__iexact=name, 
            phone=phone.strip()
        ).first()
    else:
        # Match by name only where phone is empty/null
        return Customer.objects.filter(
            name__iexact=name,
            phone__in=['', None]
        ).first()

class HomeView(TemplateView):
    template_name = 'rental_scheduler/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'GTS Rental Scheduler'
        return context

# Create your views here.

class SystemSettingsUpdateView(UpdateView):
    model = SystemSettings
    template_name = 'rental_scheduler/settings_form.html'
    fields = ['winch_price', 'hitch_bar_price', 'furniture_blanket_price', 'strap_chain_price', 
              'evening_pickup_price', 'tax_rate', 'license_scan_path']
    success_url = reverse_lazy('rental_scheduler:settings_update')
    
    def get_object(self):
        # Get or create the single instance
        settings, created = SystemSettings.objects.get_or_create(
            defaults={
                'winch_price': 0.00,
                'hitch_bar_price': 0.00,
                'furniture_blanket_price': 0.00,
                'strap_chain_price': 0.00,
                'evening_pickup_price': 0.00,
                'tax_rate': 0.00,
                'license_scan_path': 'licenses/'
            }
        )
        return settings
    
    def form_valid(self, form):
        try:
            # Validate tax rate is between 0 and 100
            tax_rate = form.cleaned_data['tax_rate']
            if not 0 <= tax_rate <= 100:
                form.add_error('tax_rate', 'Tax rate must be between 0 and 100')
                return self.form_invalid(form)
            
            # Validate price fields are non-negative
            price_fields = ['winch_price', 'hitch_bar_price', 'furniture_blanket_price', 
                           'strap_chain_price', 'evening_pickup_price']
            for field in price_fields:
                value = form.cleaned_data[field]
                if value < 0:
                    form.add_error(field, f'{field.replace("_", " ").title()} cannot be negative')
                    return self.form_invalid(form)
            
            # Validate license scan path is not empty
            license_scan_path = form.cleaned_data['license_scan_path']
            if not license_scan_path:
                form.add_error('license_scan_path', 'License scan path cannot be empty')
                return self.form_invalid(form)
            
            response = super().form_valid(form)
            messages.success(self.request, 'System settings updated successfully.')
            return response
            
        except ValidationError as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'System Settings'
        return context

class TrailerCategoryListView(ListView):
    model = TrailerCategory
    template_name = 'rental_scheduler/category_list.html'
    context_object_name = 'categories'
    ordering = ['category']  # Sort by category name by default
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Trailer Categories'
        return context

class TrailerCategoryCreateView(CreateView):
    model = TrailerCategory
    template_name = 'rental_scheduler/category_form.html'
    fields = ['category']
    success_url = reverse_lazy('rental_scheduler:category_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Trailer Category'
        context['button_text'] = 'Create Category'
        return context
    
    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, 'Trailer category created successfully.')
            return response
        except ValidationError as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)

class TrailerCategoryUpdateView(UpdateView):
    model = TrailerCategory
    template_name = 'rental_scheduler/category_form.html'
    fields = ['category']
    success_url = reverse_lazy('rental_scheduler:category_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Trailer Category'
        context['button_text'] = 'Update Category'
        return context
    
    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, 'Trailer category updated successfully.')
            return response
        except ValidationError as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)

class TrailerCategoryDeleteView(DeleteView):
    model = TrailerCategory
    template_name = 'rental_scheduler/components/confirm_delete.html'
    success_url = reverse_lazy('rental_scheduler:category_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Trailer Category'
        context['object_type'] = 'category'
        context['object_display'] = self.object.category
        context['back_url'] = 'rental_scheduler:category_list'
        context['back_text'] = 'Categories'
        
        # Get related trailers and contracts
        trailers = Trailer.objects.filter(category=self.object)
        contracts = Contract.objects.filter(category=self.object)
        
        # Set can_delete flag
        context['can_delete'] = not (trailers.exists() or contracts.exists())
        
        if not context['can_delete']:
            # Build warning message
            warning_msg = "This category cannot be deleted because it has associated items:\n"
            if trailers.exists():
                warning_msg += f"\n• {trailers.count()} Trailer{'s' if trailers.count() > 1 else ''}"
            if contracts.exists():
                warning_msg += f"\n• {contracts.count()} Contract{'s' if contracts.count() > 1 else ''}"
            warning_msg += "\n\nPlease reassign or delete these items before deleting this category."
            
            messages.warning(self.request, warning_msg)
            
        return context
    
    def delete(self, request, *args, **kwargs):
        try:
            response = super().delete(request, *args, **kwargs)
            messages.success(self.request, 'Trailer category deleted successfully.')
            return response
        except ProtectedError as e:
            # Get the protected objects from the error
            protected_objects = e.protected_objects
            
            # Count trailers and contracts
            trailers = [obj for obj in protected_objects if isinstance(obj, Trailer)]
            contracts = [obj for obj in protected_objects if isinstance(obj, Contract)]
            
            # Build detailed error message
            error_msg = "Cannot delete this category because it has associated items:\n"
            if trailers:
                error_msg += f"\n• {len(trailers)} Trailer{'s' if len(trailers) > 1 else ''}"
            if contracts:
                error_msg += f"\n• {len(contracts)} Contract{'s' if len(contracts) > 1 else ''}"
            error_msg += "\n\nPlease reassign or delete these items first."
            
            messages.error(self.request, error_msg)
            return redirect(self.success_url)

@require_http_methods(["GET"])
def browse_folders(request):
    """API endpoint to browse folders for license scan path selection."""
    try:
        # Get the base path from query parameters, default to current directory
        base_path = request.GET.get('path', os.getcwd())
        
        # Convert to absolute path if relative
        base_path = os.path.abspath(base_path)
        
        # Check if this is a network path
        is_network_path = base_path.startswith('\\\\') or base_path.startswith('//')
        
        # Validate network path if it is one
        if is_network_path:
            try:
                # Try to access the path
                if not os.path.exists(base_path):
                    return JsonResponse({
                        'error': f'Network path is not accessible: {base_path}',
                        'is_network_path': True
                    }, status=400)
                
                # Try to create a test file
                test_file = os.path.join(base_path, '.test')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
            except Exception as e:
                return JsonResponse({
                    'error': f'Network path validation failed: {str(e)}',
                    'is_network_path': True
                }, status=400)
        
        # Get list of directories
        items = []
        if os.path.exists(base_path):
            try:
                for item in os.listdir(base_path):
                    full_path = os.path.join(base_path, item)
                    if os.path.isdir(full_path):
                        # For network paths, we need to check accessibility
                        if is_network_path:
                            try:
                                # Try to access the directory
                                test_file = os.path.join(full_path, '.test')
                                with open(test_file, 'w') as f:
                                    f.write('test')
                                os.remove(test_file)
                            except Exception:
                                # Skip directories that aren't accessible
                                continue
                        
                        items.append({
                            'name': item,
                            'path': full_path,
                            'is_dir': True,
                            'is_network_path': is_network_path
                        })
                
                # Sort directories alphabetically
                items.sort(key=lambda x: x['name'].lower())
                
                # Get parent directory for navigation
                parent_path = os.path.dirname(base_path)
                if parent_path != base_path:  # Don't add parent for root
                    items.insert(0, {
                        'name': '..',
                        'path': parent_path,
                        'is_dir': True,
                        'is_network_path': parent_path.startswith('\\\\') or parent_path.startswith('//')
                    })
                
                return JsonResponse({
                    'current_path': base_path,
                    'items': items,
                    'is_network_path': is_network_path
                })
            except Exception as e:
                return JsonResponse({
                    'error': f'Error listing directory: {str(e)}',
                    'is_network_path': is_network_path
                }, status=500)
        else:
            return JsonResponse({
                'error': f'Path does not exist: {base_path}',
                'is_network_path': is_network_path
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'is_network_path': False
        }, status=500)

@require_http_methods(["GET"])
def validate_network_path(request):
    """API endpoint to validate a network path."""
    logger.info(f"Validating network path: {request.GET.get('path')}")
    
    try:
        path = request.GET.get('path')
        if not path:
            return JsonResponse({'error': 'Path is required'}, status=400)
            
        # Use our new validation function
        is_valid, is_network_path, error_message = validate_network(path)
        
        # Set appropriate response based on validation
        if is_valid:
            logger.info(f"Network path validation successful: {path}")
            return JsonResponse({
                'valid': True,
                'is_network_path': is_network_path,
                'path': path
            })
        else:
            # Send the error but still allow continuation with a 200
            logger.warning(f"Network path validation failed: {error_message}")
            return JsonResponse({
                'valid': False,
                'is_network_path': is_network_path,
                'error': error_message or "Network path could not be validated",
                'details': "You can still proceed if you believe this path should be accessible.",
                'path': path
            }, status=200)
            
    except Exception as e:
        logger.error(f"Unexpected error validating network path: {str(e)}")
        return JsonResponse({
            'error': f"Unexpected error: {str(e)}",
            'is_network_path': path.startswith('\\\\') if path else False,
            'valid': False,
            'details': str(e)
        }, status=200)

@require_http_methods(["GET"])
def get_network_status(request):
    """API endpoint to check network path status."""
    try:
        settings = SystemSettings.objects.first()
        if not settings:
            return JsonResponse({
                'error': 'System settings not found',
                'has_settings': False
            }, status=404)
            
        return JsonResponse({
            'has_settings': True,
            'is_network_path': settings.is_network_path,
            'path_validation_status': settings.path_validation_status,
            'last_path_validation': settings.last_path_validation.isoformat() if settings.last_path_validation else None,
            'path_validation_error': settings.path_validation_error,
            'license_scan_path': settings.license_scan_path
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'has_settings': False
        }, status=500)

class TrailerListView(ListView):
    model = Trailer
    template_name = 'rental_scheduler/trailer_list.html'
    context_object_name = 'trailers'
    
    def get_filtered_queryset(self):
        """Apply category and search filters to queryset"""
        queryset = Trailer.objects.select_related('category').prefetch_related('trailerservice_set')
        
        # Apply category filter
        category_id = self.request.GET.get('category')
        if category_id:
            try:
                category_id = int(category_id)
                queryset = queryset.filter(category_id=category_id)
            except (ValueError, TypeError):
                pass  # Invalid category ID, ignore filter
        
        # Apply search filter
        search_term = self.request.GET.get('search', '').strip()
        if search_term:
            queryset = self.get_search_queryset(queryset, search_term)
        
        return queryset
    
    def get_search_queryset(self, queryset, search_term):
        """Apply search logic for number and size"""
        from django.db.models import Q
        
        # Search in trailer number (case-insensitive partial match)
        number_q = Q(number__icontains=search_term)
        
        # Initialize size query
        size_q = Q()
        
        # Handle dimension searches with 'x' (like "16x", "12x6", "16x8")
        if 'x' in search_term.lower():
            try:
                parts = search_term.lower().replace(' ', '').split('x')
                if len(parts) == 2:
                    length_str, width_str = parts
                    
                    # Handle complete dimension searches like "16x8"
                    if length_str and width_str:
                        try:
                            length_val = float(length_str)
                            width_val = float(width_str)
                            size_q |= Q(length=length_val, width=width_val)
                        except ValueError:
                            pass
                    
                    # Handle partial dimension searches like "16x" (any width)
                    elif length_str and not width_str:
                        try:
                            length_val = float(length_str)
                            size_q |= Q(length=length_val)
                        except ValueError:
                            pass
                    
                    # Handle partial dimension searches like "x8" (any length)
                    elif not length_str and width_str:
                        try:
                            width_val = float(width_str)
                            size_q |= Q(width=width_val)
                        except ValueError:
                            pass
            except:
                pass
        else:
            # For non-'x' searches, try to match individual dimensions
            try:
                dimension_val = float(search_term)
                size_q = Q(length=dimension_val) | Q(width=dimension_val)
            except ValueError:
                # Not a number, skip dimension search
                pass
        
        # Combine all search conditions
        combined_q = number_q | size_q
        return queryset.filter(combined_q)
    
    def get_queryset(self):
        # Get filtered queryset
        trailers = list(self.get_filtered_queryset())
        
        # Sort by category name first, then length, then width
        trailers.sort(key=lambda t: (
            t.category.category.lower(),  # Category name (case-insensitive)
            float(t.length or 0),         # Length in feet
            float(t.width or 0)           # Width in feet
        ))
        
        return trailers
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Trailers'
        
        # Add categories for filter dropdown
        context['categories'] = TrailerCategory.objects.all().order_by('category')
        
        # Add current filter values
        context['current_category'] = self.request.GET.get('category', '')
        context['current_search'] = self.request.GET.get('search', '')
        
        # Add results count for user feedback
        context['results_count'] = len(context['trailers'])
        
        return context
    
    def render_to_response(self, context, **response_kwargs):
        """Handle both full page and HTMX partial responses"""
        # Check if this is an HTMX request for partial update
        if self.request.headers.get('HX-Request'):
            # Return only the table rows for HTMX update
            return render(self.request, 'rental_scheduler/partials/trailer_table_rows.html', context)
        
        # Return full page for normal requests
        return super().render_to_response(context, **response_kwargs)

class TrailerCreateView(CreateView):
    model = Trailer
    template_name = 'rental_scheduler/trailer_form.html'
    fields = [
        'category', 'number', 'length', 'width', 'model', 'hauling_capacity',
        'half_day_rate', 'daily_rate', 'weekly_rate', 'is_available'
    ]
    success_url = reverse_lazy('rental_scheduler:trailer_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Trailer'
        context['button_text'] = 'Create Trailer'
        return context
    
    def form_valid(self, form):
        try:
            # Validate rates are non-negative
            for field in ['half_day_rate', 'daily_rate', 'weekly_rate']:
                if form.cleaned_data[field] < 0:
                    form.add_error(field, f'{field.replace("_", " ").title()} cannot be negative')
                    return self.form_invalid(form)

            
            response = super().form_valid(form)
            messages.success(self.request, 'Trailer created successfully.')
            return response
        except ValidationError as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)

class TrailerUpdateView(UpdateView):
    model = Trailer
    template_name = 'rental_scheduler/trailer_form.html'
    fields = [
        'category', 'number', 'length', 'width', 'model', 'hauling_capacity',
        'half_day_rate', 'daily_rate', 'weekly_rate', 'is_available'
    ]
    success_url = reverse_lazy('rental_scheduler:trailer_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Trailer'
        context['button_text'] = 'Update Trailer'
        return context
    
    def form_valid(self, form):
        try:
            # Validate rates are non-negative
            for field in ['half_day_rate', 'daily_rate', 'weekly_rate']:
                if form.cleaned_data[field] < 0:
                    form.add_error(field, f'{field.replace("_", " ").title()} cannot be negative')
                    return self.form_invalid(form)
            
            response = super().form_valid(form)
            messages.success(self.request, 'Trailer updated successfully.')
            return response
        except ValidationError as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)

class TrailerDeleteView(DeleteView):
    model = Trailer
    template_name = 'rental_scheduler/components/confirm_delete.html'
    success_url = reverse_lazy('rental_scheduler:trailer_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Trailer'
        context['object_type'] = 'trailer'
        context['object_display'] = f"{self.object.number} - {self.object.model}"
        context['back_url'] = 'rental_scheduler:trailer_list'
        context['back_text'] = 'Trailers'
        
        # Get related contracts
        contracts = Contract.objects.filter(trailer=self.object)
        
        # Set can_delete flag
        context['can_delete'] = not contracts.exists()
        
        if not context['can_delete']:
            # Build warning message
            warning_msg = "This trailer cannot be deleted because it has associated items:\n"
            warning_msg += f"\n• {contracts.count()} Contract{'s' if contracts.count() > 1 else ''}"
            warning_msg += "\n\nPlease delete these contracts first."
            
            messages.warning(self.request, warning_msg)
            
        return context
    
    def delete(self, request, *args, **kwargs):
        try:
            response = super().delete(request, *args, **kwargs)
            messages.success(self.request, 'Trailer deleted successfully.')
            return response
        except ProtectedError as e:
            # Get the protected objects from the error
            protected_objects = e.protected_objects
            
            # Count contracts
            contracts = [obj for obj in protected_objects if isinstance(obj, Contract)]
            
            # Build detailed error message
            error_msg = "Cannot delete this trailer because it has associated items:\n"
            if contracts:
                error_msg += f"\n• {len(contracts)} Contract{'s' if len(contracts) > 1 else ''}"
            error_msg += "\n\nPlease delete these contracts first."
            
            messages.error(self.request, error_msg)
            return redirect(self.success_url)

class TrailerServiceForm(forms.ModelForm):
    start_datetime = forms.DateTimeField(
        input_formats=['%m/%d/%Y %I:%M %p'],
        widget=forms.DateTimeInput(
            attrs={'class': 'datepicker'},
            format='%m/%d/%Y %I:%M %p'
        )
    )
    
    end_datetime = forms.DateTimeField(
        input_formats=['%m/%d/%Y %I:%M %p'],
        widget=forms.DateTimeInput(
            attrs={'class': 'datepicker'},
            format='%m/%d/%Y %I:%M %p'
        )
    )
    
    class Meta:
        model = TrailerService
        fields = ['start_datetime', 'end_datetime', 'description']

class TrailerServiceCreateView(CreateView):
    model = TrailerService
    form_class = TrailerServiceForm
    template_name = 'rental_scheduler/service_form.html'
    
    def get_success_url(self):
        return reverse_lazy('rental_scheduler:trailer_service_management', kwargs={'trailer_pk': self.kwargs['trailer_pk']})
    
    def get_object_trailer(self):
        """Get the trailer this service is for"""
        return get_object_or_404(Trailer, pk=self.kwargs['trailer_pk'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trailer = self.get_object_trailer()
        context['title'] = f'Add New Service for {trailer.number}'
        context['button_text'] = 'Schedule Service'
        context['trailer'] = trailer
        context['back_url'] = reverse_lazy('rental_scheduler:trailer_service_management', kwargs={'trailer_pk': trailer.pk})
        context['is_add_form'] = True
        return context
    
    def form_valid(self, form):
        try:
            trailer = self.get_object_trailer()
            form.instance.trailer = trailer
            
            # Get form data
            start_dt = form.cleaned_data['start_datetime']
            end_dt = form.cleaned_data['end_datetime']
            
            # Make timezone-aware if needed
            if timezone.is_naive(start_dt):
                start_dt = timezone.make_aware(start_dt)
            if timezone.is_naive(end_dt):
                end_dt = timezone.make_aware(end_dt)
            
            form.instance.start_datetime = start_dt
            form.instance.end_datetime = end_dt
            
            # Check for conflicts with existing services
            overlapping_services = TrailerService.objects.filter(
                trailer=trailer,
                start_datetime__lt=end_dt,
                end_datetime__gt=start_dt
            )
            
            # Exclude current instance if updating (for the update view)
            if hasattr(form.instance, 'pk') and form.instance.pk:
                overlapping_services = overlapping_services.exclude(pk=form.instance.pk)
            
            # Check for conflicts with existing contracts
            conflicting_contracts = Contract.objects.filter(
                trailer=trailer,
                start_datetime__lt=end_dt,
                end_datetime__gt=start_dt
            ).select_related('customer')
            
            # Handle service conflicts
            if overlapping_services.exists():
                service_conflict = overlapping_services.first()
                conflict_start = format_local(service_conflict.start_datetime)
                conflict_end = format_local(service_conflict.end_datetime)
                conflict_desc = service_conflict.description or "Maintenance"
                
                form.add_error(None, 
                    f"⚠️ Service Time Conflict\n\n"
                    f"This time period overlaps with an existing service:\n\n"
                    f"• Service: {conflict_desc}\n"
                    f"• Period: {conflict_start} to {conflict_end}\n\n"
                    f"Please choose a different time that doesn't conflict with existing services."
                )
                return self.form_invalid(form)
            
            # If conflicts exist and user hasn't confirmed, show warning
            force_create = self.request.POST.get('force_create') == 'true'
            
            if conflicting_contracts.exists() and not force_create:
                # Build detailed conflict message
                conflict_details = []
                for contract in conflicting_contracts:
                    conflict_details.append({
                        'id': contract.id,
                        'customer_name': contract.customer.name,
                        'customer_phone': contract.customer.phone or 'No phone',
                        'start_datetime': format_local(contract.start_datetime),
                        'end_datetime': format_local(contract.end_datetime),
                        'is_picked_up': contract.is_picked_up,
                        'is_returned': contract.is_returned
                    })
                
                # Add conflict data to form for template rendering
                form.conflicts = conflict_details
                form.show_conflict_warning = True
                return self.form_invalid(form)
            
            # Proceed with normal validation and save
            response = super().form_valid(form)
            
            # Show simple success message
            messages.success(self.request, f'Service scheduled for {trailer.number} successfully.')
            
            return response
        except ValidationError as e:
            # Handle model validation errors gracefully
            if hasattr(e, 'message_dict'):
                # Field-specific errors
                for field, errors in e.message_dict.items():
                    for error in errors:
                        form.add_error(field, error)
            else:
                # Non-field errors (like our improved service conflict message)
                form.add_error(None, str(e.message) if hasattr(e, 'message') else str(e))
            return self.form_invalid(form)

class TrailerServiceUpdateView(UpdateView):
    model = TrailerService
    form_class = TrailerServiceForm
    template_name = 'rental_scheduler/service_form.html'
    
    def get_success_url(self):
        return reverse_lazy('rental_scheduler:trailer_service_management', kwargs={'trailer_pk': self.object.trailer.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Update Service for {self.object.trailer.number}'
        context['button_text'] = 'Update Service'
        context['trailer'] = self.object.trailer
        context['back_url'] = reverse_lazy('rental_scheduler:trailer_service_management', kwargs={'trailer_pk': self.object.trailer.pk})
        context['is_add_form'] = False
        return context
    
    def form_valid(self, form):
        try:
            trailer = self.object.trailer
            
            # Get form data
            start_dt = form.cleaned_data['start_datetime']
            end_dt = form.cleaned_data['end_datetime']
            
            # Make timezone-aware if needed
            if timezone.is_naive(start_dt):
                start_dt = timezone.make_aware(start_dt)
            if timezone.is_naive(end_dt):
                end_dt = timezone.make_aware(end_dt)
            
            form.instance.start_datetime = start_dt
            form.instance.end_datetime = end_dt
            
            # Check for conflicts with existing services (exclude current service)
            overlapping_services = TrailerService.objects.filter(
                trailer=trailer,
                start_datetime__lt=end_dt,
                end_datetime__gt=start_dt
            ).exclude(pk=self.object.pk)
            
            # Check for conflicts with existing contracts
            conflicting_contracts = Contract.objects.filter(
                trailer=trailer,
                start_datetime__lt=end_dt,
                end_datetime__gt=start_dt
            ).select_related('customer')
            
            # Handle service conflicts
            if overlapping_services.exists():
                service_conflict = overlapping_services.first()
                conflict_start = format_local(service_conflict.start_datetime)
                conflict_end = format_local(service_conflict.end_datetime)
                conflict_desc = service_conflict.description or "Maintenance"
                
                form.add_error(None, 
                    f"⚠️ Service Time Conflict\n\n"
                    f"This time period overlaps with an existing service:\n\n"
                    f"• Service: {conflict_desc}\n"
                    f"• Period: {conflict_start} to {conflict_end}\n\n"
                    f"Please choose a different time that doesn't conflict with existing services."
                )
                return self.form_invalid(form)
            
            # If conflicts exist and user hasn't confirmed, show warning
            force_create = self.request.POST.get('force_create') == 'true'
            
            if conflicting_contracts.exists() and not force_create:
                # Build detailed conflict message
                conflict_details = []
                for contract in conflicting_contracts:
                    conflict_details.append({
                        'id': contract.id,
                        'customer_name': contract.customer.name,
                        'customer_phone': contract.customer.phone or 'No phone',
                        'start_datetime': format_local(contract.start_datetime),
                        'end_datetime': format_local(contract.end_datetime),
                        'is_picked_up': contract.is_picked_up,
                        'is_returned': contract.is_returned
                    })
                
                # Add conflict data to form for template rendering
                form.conflicts = conflict_details
                form.show_conflict_warning = True
                return self.form_invalid(form)
            
            # Proceed with normal validation and save
            response = super().form_valid(form)
            
            # Show simple success message
            messages.success(self.request, f'Service for {trailer.number} updated successfully.')
            
            return response
        except ValidationError as e:
            # Handle model validation errors gracefully
            if hasattr(e, 'message_dict'):
                # Field-specific errors
                for field, errors in e.message_dict.items():
                    for error in errors:
                        form.add_error(field, error)
            else:
                # Non-field errors (like our improved service conflict message)
                form.add_error(None, str(e.message) if hasattr(e, 'message') else str(e))
            return self.form_invalid(form)

@require_http_methods(["POST"])
def end_service_early(request, pk):
    """End a trailer service early"""
    try:
        service = get_object_or_404(TrailerService, pk=pk)
        
        # Store original end time for message
        original_end_time = service.end_datetime
        trailer_pk = service.trailer.pk
        
        # Set end time to now
        service.end_datetime = timezone.now()
        service.save()
        
        # Create detailed success message
        original_end_str = original_end_time.strftime('%m/%d/%Y %I:%M %p')
        current_time_str = timezone.now().strftime('%m/%d/%Y %I:%M %p')
        messages.success(
            request, 
            f'✅ Trailer {service.trailer.number} is now AVAILABLE!\n\n'
            f'Service ended early at {current_time_str}\n'
            f'(Originally scheduled to end: {original_end_str})\n\n'
            f'The trailer can now be rented again.'
        )
        return redirect('rental_scheduler:trailer_service_management', trailer_pk=trailer_pk)
        
    except Exception as e:
        messages.error(request, f'Error ending service: {str(e)}')
        return redirect('rental_scheduler:trailer_list')

class TrailerServiceDeleteView(DeleteView):
    model = TrailerService
    template_name = 'rental_scheduler/components/confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('rental_scheduler:trailer_service_management', kwargs={'trailer_pk': self.object.trailer.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Service'
        context['object_type'] = 'service'
        context['object_display'] = f'Service for {self.object.trailer.number}'
        context['back_url'] = reverse_lazy('rental_scheduler:trailer_service_management', kwargs={'trailer_pk': self.object.trailer.pk})
        context['back_text'] = 'Service Management'
        context['can_delete'] = True
        return context
    
    def delete(self, request, *args, **kwargs):
        try:
            trailer_number = self.object.trailer.number
            trailer_pk = self.object.trailer.pk
            response = super().delete(request, *args, **kwargs)
            messages.success(self.request, f'Service for {trailer_number} deleted successfully.')
            return response
        except Exception as e:
            messages.error(self.request, f'Error deleting service: {str(e)}')
            return redirect(reverse_lazy('rental_scheduler:trailer_service_management', kwargs={'trailer_pk': trailer_pk}))

class ContractListView(ListView):
    model = Contract
    template_name = 'rental_scheduler/contract_list.html'
    context_object_name = 'contracts'
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('customer')
        
        # Get month and year from query parameters, default to current month
        month = self.request.GET.get('month')
        year = self.request.GET.get('year')
        
        if month and year:
            # Filter by month and year
            queryset = queryset.filter(
                start_datetime__year=year,
                start_datetime__month=month
            )
        else:
            # Default to current month
            now = datetime.now()
            queryset = queryset.filter(
                start_datetime__year=now.year,
                start_datetime__month=now.month
            )
        
        # Add search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                models.Q(customer__name__icontains=search_query) |
                models.Q(customer__phone__icontains=search_query)
            )
        
        # Add sorting functionality
        sort_by = self.request.GET.get('sort', 'customer__name')  # Default to alphabetical by customer name
        sort_direction = self.request.GET.get('direction', 'asc')
        
        # Define allowed sort fields to prevent SQL injection
        allowed_sort_fields = {
            'customer__name': 'customer__name',
            'customer__state': 'customer__state', 
            'customer__city': 'customer__city',
            'customer__street_address': 'customer__street_address',
            'customer__phone': 'customer__phone',
            'start_datetime': 'start_datetime',
            'customer__drivers_license_scanned': 'customer__drivers_license_scanned'
        }
        
        if sort_by in allowed_sort_fields:
            order_field = allowed_sort_fields[sort_by]
            if sort_direction == 'desc':
                order_field = f'-{order_field}'
            queryset = queryset.order_by(order_field)
        else:
            # Default fallback to alphabetical order
            queryset = queryset.order_by('customer__name')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Contracts'
        
        # Add month/year context for navigation
        now = datetime.now()
        month = int(self.request.GET.get('month', now.month))
        year = int(self.request.GET.get('year', now.year))
        
        # Create a datetime object for the current month
        current_month_date = datetime(year=year, month=month, day=1)
        
        # Calculate previous and next month
        if month == 1:
            prev_month = 12
            prev_year = year - 1
        else:
            prev_month = month - 1
            prev_year = year
            
        if month == 12:
            next_month = 1
            next_year = year + 1
        else:
            next_month = month + 1
            next_year = year
            
        # Add sorting context
        current_sort = self.request.GET.get('sort', 'customer__name')
        current_direction = self.request.GET.get('direction', 'asc')
        
        context.update({
            'current_month': current_month_date,
            'current_year': year,
            'prev_month': prev_month,
            'prev_year': prev_year,
            'next_month': next_month,
            'next_year': next_year,
            'search_query': self.request.GET.get('search', ''),
            'current_sort': current_sort,
            'current_direction': current_direction
        })
        
        return context

class ContractDetailView(DetailView):
    model = Contract
    template_name = 'rental_scheduler/contract_detail.html'
    context_object_name = 'contract'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Contract #{self.object.id}'
        return context

@require_http_methods(["GET"])
def search_customers(request):
    """API endpoint to search for customers by name or phone with deduplication"""
    query = request.GET.get('query', '').strip()
    
    if not query:
        return JsonResponse({'customers': []})
    
    # Get all matching customers
    customers = Customer.objects.filter(
        models.Q(name__icontains=query) |
        models.Q(phone__icontains=query)
    ).order_by('-updated_at')  # Prefer most recently updated
    
    # Deduplicate by (name, phone) combination
    seen = set()
    unique_customers = []
    
    for customer in customers:
        # Create key for deduplication (case-insensitive name, normalized phone)
        key = (customer.name.lower().strip(), (customer.phone or '').strip())
        
        if key not in seen:
            seen.add(key)
            unique_customers.append({
                'id': customer.id,
                'name': customer.name,
                'phone': customer.phone,
                'street_address': customer.street_address,
                'city': customer.city,
                'state': customer.state,
                'zip_code': customer.zip_code,
                'po_number': customer.po_number,
                'drivers_license_scanned': customer.drivers_license_scanned,
                'drivers_license_number': customer.drivers_license_number
            })
            
            # Limit to 25 unique results
            if len(unique_customers) >= 25:
                break
    
    return JsonResponse({'customers': unique_customers})

class ContractForm(forms.ModelForm):
    # Customer fields
    customer_id = forms.IntegerField(required=False, widget=forms.HiddenInput())
    customer_name = forms.CharField(max_length=200)
    customer_phone = forms.CharField(max_length=20, required=False)
    customer_street_address = forms.CharField(max_length=200, required=False)
    customer_city = forms.CharField(max_length=100, required=False)
    customer_state = forms.CharField(max_length=2, required=False)
    customer_zip_code = forms.CharField(max_length=10, required=False)
    customer_po_number = forms.CharField(max_length=50, required=False)
    customer_drivers_license_number = forms.CharField(
        max_length=50,
        required=False,
        help_text="Customer's driver's license number"
    )
    customer_drivers_license_scan = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'accept': '.pdf,.jpg,.jpeg,.png'})
    )
    current_license_path = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        help_text="Current path of the uploaded license file"
    )

    # Explicitly define datetime fields with input formats
    start_datetime = forms.DateTimeField(
        input_formats=['%m/%d/%Y %I:%M %p'],
        widget=forms.DateTimeInput(
            attrs={'class': 'datepicker'},
            format='%m/%d/%Y %I:%M %p'
        )
    )
    
    end_datetime = forms.DateTimeField(
        input_formats=['%m/%d/%Y %I:%M %p'],
        widget=forms.DateTimeInput(
            attrs={'class': 'datepicker'},
            format='%m/%d/%Y %I:%M %p'
        )
    )

    return_datetime = forms.DateTimeField(
        required=False,
        input_formats=['%m/%d/%Y %I:%M %p'],
        widget=forms.DateTimeInput(
            attrs={'class': 'datepicker'},
            format='%m/%d/%Y %I:%M %p'
        )
    )

    furniture_blanket_count = forms.IntegerField(
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={'min': '0', 'step': '1', 'placeholder': '0'})
    )
    
    strap_chain_count = forms.IntegerField(
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={'min': '0', 'step': '1', 'placeholder': '0'})
    )
    
    # Override extra_mileage and down_payment to show empty instead of 0
    extra_mileage = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'min': '0', 'step': '0.01', 'placeholder': '0'}),
        help_text="Additional charges for extra mileage"
    )
    
    down_payment = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'min': '0', 'step': '0.01', 'placeholder': '0'}),
        help_text="Initial payment amount"
    )
    
    # Override payment_type to remove empty option
    payment_type = forms.ChoiceField(
        choices=[('cash', 'Cash Payment'), ('charge', 'Charge Payment')],
        widget=forms.RadioSelect(),
        required=True,
        help_text="Type of payment accepted"
    )

    class Meta:
        model = Contract
        fields = [
            'customer_id',  # Add this to the fields list
            # Rental Details
            'start_datetime', 'end_datetime', 'category', 'trailer',
            # Add-on Features
            'includes_winch', 'includes_hitch_bar', 
            'furniture_blanket_count', 'strap_chain_count', 'has_evening_pickup',
            # Rate Details
            'custom_rate', 'extra_mileage',
            # Financial Information
            'down_payment',
            # Status Management
            'show_in_calendar', 'payment_type', 'payment_timing',
            'is_picked_up', 'is_returned', 'return_datetime',
            'is_billed', 'is_invoiced'
        ]
        widgets = {
            'payment_timing': forms.RadioSelect(),
            'includes_hitch_bar': forms.CheckboxInput(),
            'has_evening_pickup': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If we have an instance, populate the customer fields
        if self.instance and self.instance.pk:
            if hasattr(self.instance, 'customer'):
                customer = self.instance.customer
                self.fields['customer_id'].initial = customer.id
                self.fields['customer_name'].initial = customer.name
                self.fields['customer_phone'].initial = customer.phone
                self.fields['customer_street_address'].initial = customer.street_address
                self.fields['customer_city'].initial = customer.city
                self.fields['customer_state'].initial = customer.state
                self.fields['customer_zip_code'].initial = customer.zip_code
                self.fields['customer_po_number'].initial = customer.po_number
                self.fields['customer_drivers_license_number'].initial = customer.drivers_license_number
                
                # Set the current license path if it exists
                if customer.drivers_license_scan:
                    self.fields['current_license_path'].initial = customer.drivers_license_scan.name
            
        # Set initial values for payment fields
        self.fields['payment_timing'].initial = 'pickup'
        
        # Remove empty option from payment_timing radio field
        self.fields['payment_timing'].empty_label = None
        
        # For existing instances, show empty instead of 0 for extra_mileage and down_payment
        if self.instance and self.instance.pk:
            if self.instance.extra_mileage == 0:
                self.fields['extra_mileage'].initial = None
            if self.instance.down_payment == 0:
                self.fields['down_payment'].initial = None
            if self.instance.furniture_blanket_count == 0:
                self.fields['furniture_blanket_count'].initial = None
            if self.instance.strap_chain_count == 0:
                self.fields['strap_chain_count'].initial = None

    def clean(self):
        cleaned_data = super().clean()
        start_datetime = cleaned_data.get('start_datetime')
        end_datetime = cleaned_data.get('end_datetime')

        # Make all datetime fields timezone-aware
        if start_datetime:
            if timezone.is_naive(start_datetime):
                cleaned_data['start_datetime'] = timezone.make_aware(start_datetime)

        if end_datetime:
            if timezone.is_naive(end_datetime):
                cleaned_data['end_datetime'] = timezone.make_aware(end_datetime)

        if cleaned_data.get('return_datetime'):
            if timezone.is_naive(cleaned_data['return_datetime']):
                cleaned_data['return_datetime'] = timezone.make_aware(cleaned_data['return_datetime'])

        # Validate end datetime is after start datetime
        if start_datetime and end_datetime and end_datetime <= start_datetime:
            self.add_error('end_datetime', 'End date/time must be after start date/time.')
        
        # Convert empty numeric fields to 0
        if cleaned_data.get('extra_mileage') is None:
            cleaned_data['extra_mileage'] = 0
        if cleaned_data.get('down_payment') is None:
            cleaned_data['down_payment'] = 0
        if cleaned_data.get('furniture_blanket_count') is None:
            cleaned_data['furniture_blanket_count'] = 0
        if cleaned_data.get('strap_chain_count') is None:
            cleaned_data['strap_chain_count'] = 0
            
        return cleaned_data

    def clean_customer_drivers_license_scan(self):
        file = self.cleaned_data.get('customer_drivers_license_scan')
        if file:
            logger.info(f"Processing file upload: {file.name}")
            # Get file extension
            ext = os.path.splitext(file.name)[1].lower()
            
            # Validate file type
            allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
            if ext not in allowed_extensions:
                logger.warning(f"Invalid file extension: {ext}")
                raise forms.ValidationError(
                    f"Only {', '.join(allowed_extensions)} files are allowed"
                )
            
            # Validate file size (5MB max)
            if file.size > 5 * 1024 * 1024:
                logger.warning(f"File too large: {file.size} bytes")
                raise forms.ValidationError(
                    "File size cannot exceed 5MB"
                )
            
            # Ensure settings path exists
            try:
                settings = SystemSettings.objects.first()
                if settings and settings.license_scan_path:
                    logger.info(f"License scan path from settings: {settings.license_scan_path}")
                    if not os.path.exists(settings.license_scan_path):
                        logger.error(f"License scan path does not exist: {settings.license_scan_path}")
                        raise forms.ValidationError(
                            "License scan path is not properly configured. Please contact administrator."
                        )
                else:
                    logger.warning("No license scan path configured in settings")
            except Exception as e:
                logger.error(f"Error checking license scan path: {str(e)}")
                raise forms.ValidationError(
                    "Unable to validate license scan path. Please contact administrator."
                )
                
        return file

    def save(self, commit=True):
        logger.info("Starting ContractForm.save()")
        # First save the customer
        customer_data = {
            'name': self.cleaned_data.get('customer_name', ''),
            'phone': self.cleaned_data.get('customer_phone', ''),
            'street_address': self.cleaned_data.get('customer_street_address', ''),
            'city': self.cleaned_data.get('customer_city', ''),
            'state': self.cleaned_data.get('customer_state', ''),
            'zip_code': self.cleaned_data.get('customer_zip_code', ''),
            'po_number': self.cleaned_data.get('customer_po_number', ''),
            'drivers_license_number': self.cleaned_data.get('customer_drivers_license_number', ''),
        }
        
        # Ensure name is not empty (required field)
        if not customer_data['name']:
            raise ValueError("Customer name is required")

        # Handle the customer creation/update with smart deduplication
        customer_id = self.cleaned_data.get('customer_id')
        if customer_id:  # This will be falsy for None, empty string, or 0
            logger.info(f"Updating existing customer with ID: {customer_id}")
            customer = Customer.objects.get(id=customer_id)
            for key, value in customer_data.items():
                setattr(customer, key, value)
        else:
            # Smart lookup to prevent duplicates
            logger.info("Looking for existing customer to prevent duplicates")
            existing_customer = find_existing_customer(
                customer_data['name'], 
                customer_data['phone']
            )
            
            if existing_customer:
                logger.info(f"Found existing customer: {existing_customer.id} - {existing_customer.name}")
                customer = existing_customer
                # Update existing customer with any new information
                for key, value in customer_data.items():
                    setattr(customer, key, value)
            else:
                logger.info("Creating new customer - no duplicates found")
                customer = Customer(**customer_data)

        # For faster contract creation, defer license file processing
        license_scan = self.cleaned_data.get('customer_drivers_license_scan')
        process_license_later = False
        
        if license_scan:
            logger.info(f"License file detected: {license_scan.name}, will process after contract creation")
            process_license_later = True
        elif self.cleaned_data.get('current_license_path'):
            logger.info(f"Keeping existing license file: {self.cleaned_data['current_license_path']}")
            customer.drivers_license_scanned = True

        # Now save the contract
        contract = super().save(commit=False)
        contract.customer = customer

        if commit:
            # Use transaction to ensure both customer and contract are saved together
            with transaction.atomic():
                # Always save the customer (whether new or existing)
                customer.save()
                # Save the contract first (faster response)
                contract.save()
                # Save any many-to-many relationships
                self.save_m2m()
                
                # Process license file asynchronously if needed
                if process_license_later:
                    self._process_license_file_async(customer, license_scan)

        return contract
    
    def _process_license_file_async(self, customer, license_scan):
        """Process license file upload asynchronously to avoid blocking contract creation"""
        try:
            logger.info(f"Processing license scan file asynchronously: {license_scan.name}")
            
            # Delete old file if it exists
            if customer.drivers_license_scan:
                try:
                    old_file_path = customer.drivers_license_scan.path
                    if os.path.exists(old_file_path):
                        logger.info(f"Deleting old license file: {old_file_path}")
                        os.remove(old_file_path)
                        customer.drivers_license_scan.delete(save=False)
                except Exception as e:
                    logger.warning(f"Error deleting old license file: {str(e)}")
            
            # Use the storage class to handle the file saving
            settings = SystemSettings.objects.first()
            if settings and settings.is_network_path:
                logger.info("Using network path for license scan storage")
                from rental_scheduler.models import get_license_upload_path
                
                # Generate path but don't save to the field yet
                file_path = get_license_upload_path(customer, license_scan.name)
                
                # Use storage to save the file
                storage = customer.drivers_license_scan.field.storage
                
                # Save the file through the storage interface
                saved_name = storage._save(file_path, license_scan)
                logger.info(f"License scan saved to: {saved_name}")
                
                # Update the field value to the saved path
                customer.drivers_license_scan.name = saved_name
                customer.drivers_license_scanned = True
                
                # Save the customer again with the updated field
                customer.save(update_fields=['drivers_license_scan', 'drivers_license_scanned'])
            else:
                # For regular local paths, use the normal Django field handling
                logger.info("Using regular path for license scan storage")
                customer.drivers_license_scan = license_scan
                customer.drivers_license_scanned = True
                customer.save()
                
            logger.info("Successfully saved license scan file asynchronously")
        except Exception as e:
            logger.error(f"Error saving license scan file asynchronously: {str(e)}")
            # Continue without failing the contract creation

class ContractCreateView(CreateView):
    model = Contract
    template_name = 'rental_scheduler/contract_form.html'
    form_class = ContractForm
    
    def get_success_url(self):
        # Get the next URL from the form data or default to contract list
        next_url = self.request.POST.get('next')
        if next_url:
            return next_url
        return reverse_lazy('rental_scheduler:contract_list')
    
    def get_initial(self):
        """
        Pre-populate form fields from query parameters for availability integration
        """
        initial = super().get_initial()
        
        # Handle prefill from availability page
        category_id = self.request.GET.get('category')
        trailer_id = self.request.GET.get('trailer')
        start_param = self.request.GET.get('start')
        end_param = self.request.GET.get('end')
        
        if category_id:
            try:
                category = TrailerCategory.objects.get(id=category_id)
                initial['category'] = category
            except TrailerCategory.DoesNotExist:
                pass
        
        if trailer_id:
            try:
                trailer = Trailer.objects.get(id=trailer_id)
                initial['trailer'] = trailer
            except Trailer.DoesNotExist:
                pass
        
        if start_param:
            try:
                # Parse datetime from YYYY-MM-DD HH:MM:SS format
                start_datetime = datetime.strptime(start_param, '%Y-%m-%d %H:%M:%S')
                if timezone.is_naive(start_datetime):
                    start_datetime = timezone.make_aware(start_datetime)
                initial['start_datetime'] = start_datetime
            except (ValueError, TypeError) as e:
                logger.warning(f"ContractCreateView: Invalid start datetime format: {start_param} - {e}")
        
        if end_param:
            try:
                # Parse datetime from YYYY-MM-DD HH:MM:SS format
                end_datetime = datetime.strptime(end_param, '%Y-%m-%d %H:%M:%S')
                if timezone.is_naive(end_datetime):
                    end_datetime = timezone.make_aware(end_datetime)
                initial['end_datetime'] = end_datetime
            except (ValueError, TypeError) as e:
                logger.warning(f"ContractCreateView: Invalid end datetime format: {end_param} - {e}")
        
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Contract'
        context['button_text'] = 'Create Contract'
        
        # Set the back URL based on where the user came from
        next_url = self.request.GET.get('next')
        if next_url:
            context['back_url'] = next_url
        else:
            context['back_url'] = reverse_lazy('rental_scheduler:contract_list')
        
        # Add available trailers for the selected category
        if 'category' in self.request.GET:
            category_id = self.request.GET.get('category')
            context['available_trailers'] = Trailer.objects.filter(
                category_id=category_id,
                is_available=True
            )
        else:
            context['available_trailers'] = Trailer.objects.filter(is_available=True)
            
        # Add add-on prices from settings
        try:
            settings = SystemSettings.objects.first()
            if settings:
                context['winch_price'] = settings.winch_price
                context['tax_rate'] = settings.tax_rate
                context['hitch_bar_price'] = settings.hitch_bar_price
                context['furniture_blanket_price'] = settings.furniture_blanket_price
                context['strap_chain_price'] = settings.strap_chain_price
                context['evening_pickup_price'] = settings.evening_pickup_price
            else:
                context['winch_price'] = 0
                context['tax_rate'] = 0
                context['hitch_bar_price'] = 0
                context['furniture_blanket_price'] = 0
                context['strap_chain_price'] = 0
                context['evening_pickup_price'] = 0
        except:
            context['winch_price'] = 0
            context['tax_rate'] = 0
            context['hitch_bar_price'] = 0
            context['furniture_blanket_price'] = 0
            context['strap_chain_price'] = 0
            context['evening_pickup_price'] = 0
            
        return context
    
    def form_valid(self, form):
        try:
            logger.info("Starting contract form validation")
            # Validate dates
            if form.cleaned_data['end_datetime'] <= form.cleaned_data['start_datetime']:
                logger.warning("Invalid dates: end_datetime <= start_datetime")
                form.add_error('end_datetime', 'End date must be after start date')
                return self.form_invalid(form)
            
            # Validate trailer availability
            trailer = form.cleaned_data['trailer']
            start_date = form.cleaned_data['start_datetime']
            end_date = form.cleaned_data['end_datetime']
            
            logger.info(f"Checking trailer availability: {trailer.id} from {start_date} to {end_date}")
            
            # Use centralized availability logic
            is_available, reason = is_trailer_available(trailer, start_date, end_date)
            
            if not is_available:
                logger.warning(f"Trailer {trailer.id} is not available: {reason}")
                if reason == "under_service":
                    form.add_error('trailer', 'This trailer is currently under service/maintenance during the selected dates')
                elif reason == "booked":
                    form.add_error('trailer', 'This trailer is already booked for the selected dates')
                elif reason == "not_active":
                    form.add_error('trailer', 'This trailer is not available for rental')
                else:
                    form.add_error('trailer', 'This trailer is not available for the selected dates')
                return self.form_invalid(form)
            
            # Save the contract
            logger.info("Saving contract")
            response = super().form_valid(form)
            # Only add a Django message for normal (non-AJAX) form submissions so that
            # we do not accumulate undelivered messages when this view is called
            # via the JavaScript PDF workflow.
            if self.request.headers.get('X-Requested-With') != 'XMLHttpRequest':
                messages.success(self.request, 'Contract created successfully.')
            
            # If this is an AJAX request (for PDF generation), return JSON response
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                logger.info("Handling AJAX request for PDF generation")
                return JsonResponse({
                    'status': 'success',
                    'contract_id': self.object.id
                })
            
            # If print_contract is requested, redirect to the PDF view
            if self.request.POST.get('print_contract') == 'true':
                logger.info("Redirecting to PDF view")
                return redirect('rental_scheduler:contract_pdf', pk=self.object.id)
            
            return response
            
        except ValidationError as e:
            logger.error(f"Validation error in form_valid: {str(e)}")
            form.add_error(None, str(e))
            return self.form_invalid(form)
        except Exception as e:
            logger.error(f"Unexpected error in form_valid: {str(e)}")
            raise
            
    def form_invalid(self, form):
        logger.error(f"Form validation failed: {form.errors}")
        # If this is an AJAX request, return error response
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'errors': form.errors
            }, status=400)
        return super().form_invalid(form)

class ContractUpdateView(UpdateView):
    model = Contract
    template_name = 'rental_scheduler/contract_form.html'
    form_class = ContractForm
    
    def get_success_url(self):
        # Get the next URL from the form data or default to contract list
        next_url = self.request.POST.get('next')
        if next_url:
            return next_url
        return reverse_lazy('rental_scheduler:contract_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Contract #{self.object.id}'
        context['button_text'] = 'Update Contract'
        
        # Set the back URL based on where the user came from
        next_url = self.request.GET.get('next')
        if next_url:
            context['back_url'] = next_url
        else:
            context['back_url'] = reverse_lazy('rental_scheduler:contract_list')
        
        # Add stored rate to context for JavaScript
        context['stored_rate'] = float(self.object.stored_rate) if self.object.stored_rate else None
        
        # Add available trailers for the selected category
        if self.object.category:
            # Get all available trailers in the category
            available_trailers = Trailer.objects.filter(
                models.Q(category=self.object.category, is_available=True) |
                models.Q(id=self.object.trailer.id)  # Include the current trailer
            ).distinct()
            
            context['available_trailers'] = available_trailers
        else:
            context['available_trailers'] = Trailer.objects.filter(is_available=True)
            
        # Add add-on prices from settings
        try:
            settings = SystemSettings.objects.first()
            if settings:
                context['winch_price'] = settings.winch_price
                context['tax_rate'] = settings.tax_rate
                context['hitch_bar_price'] = settings.hitch_bar_price
                context['furniture_blanket_price'] = settings.furniture_blanket_price
                context['strap_chain_price'] = settings.strap_chain_price
                context['evening_pickup_price'] = settings.evening_pickup_price
            else:
                context['winch_price'] = 0
                context['tax_rate'] = 0
                context['hitch_bar_price'] = 0
                context['furniture_blanket_price'] = 0
                context['strap_chain_price'] = 0
                context['evening_pickup_price'] = 0
        except:
            context['winch_price'] = 0
            context['tax_rate'] = 0
            context['hitch_bar_price'] = 0
            context['furniture_blanket_price'] = 0
            context['strap_chain_price'] = 0
            context['evening_pickup_price'] = 0
            
        return context
    
    def form_valid(self, form):
        try:
            # Validate dates
            if form.cleaned_data['end_datetime'] <= form.cleaned_data['start_datetime']:
                form.add_error('end_datetime', 'End date must be after start date')
                return self.form_invalid(form)
            
            # Validate trailer availability (excluding current contract)
            trailer = form.cleaned_data['trailer']
            start_date = form.cleaned_data['start_datetime']
            end_date = form.cleaned_data['end_datetime']
            logger.info(
                f"ContractUpdateView: availability check for contract={self.object.pk} "
                f"trailer={getattr(trailer, 'id', None)} "
                f"start={start_date} tz={getattr(start_date, 'tzinfo', None)} "
                f"end={end_date} tz={getattr(end_date, 'tzinfo', None)}"
            )
            
            # Use centralized availability logic, excluding current contract
            is_available, reason = is_trailer_available(trailer, start_date, end_date, exclude_contract_id=self.object.pk)
            
            if not is_available:
                logger.warning(
                    f"ContractUpdateView: not available for contract={self.object.pk}, reason={reason}"
                )
                if reason == "under_service":
                    form.add_error('trailer', 'This trailer is currently under service/maintenance during the selected dates')
                elif reason == "booked":
                    form.add_error('trailer', 'This trailer is already booked for the selected dates')
                elif reason == "not_active":
                    form.add_error('trailer', 'This trailer is not available for rental')
                else:
                    form.add_error('trailer', 'This trailer is not available for the selected dates')
                return self.form_invalid(form)
            
            # Use the form's custom save method to handle customer data properly
            contract = form.save()
            
            # The Contract model's save() method now handles pricing recalculation automatically
            # when any price-sensitive fields change, so we don't need to override it here.
            # Just let the model handle it correctly.
            contract.save()
            # Only add a Django message for normal (non-AJAX) form submissions
            if self.request.headers.get('X-Requested-With') != 'XMLHttpRequest':
                messages.success(self.request, 'Contract updated successfully.')
            
            # If this is an AJAX request (for PDF generation), return JSON response
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'contract_id': contract.id
                })
            
            return redirect(self.get_success_url())
            
        except ValidationError as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)
            
    def form_invalid(self, form):
        # If this is an AJAX request, return error response
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'errors': form.errors
            }, status=400)
        return super().form_invalid(form)

class ContractDeleteView(DeleteView):
    model = Contract
    template_name = 'rental_scheduler/components/confirm_delete.html'
    success_url = reverse_lazy('rental_scheduler:contract_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Contract'
        context['object_type'] = 'contract'
        context['object_display'] = f"Contract #{self.object.id} - {self.object.customer.name}"
        context['back_url'] = 'rental_scheduler:contract_list'
        context['back_text'] = 'Contract List'
        context['can_delete'] = True
        return context
    
    def delete(self, request, *args, **kwargs):
        try:
            response = super().delete(request, *args, **kwargs)
            messages.success(self.request, 'Contract deleted successfully.')
            return response
        except ProtectedError:
            messages.error(self.request, 'Cannot delete this contract because it has associated records.')
            return redirect(self.success_url)

@require_http_methods(["POST"])
def update_contract_status(request, pk):
    """API endpoint to update contract status (pickup/return)"""
    contract = get_object_or_404(Contract, pk=pk)
    action = request.POST.get('action')
    
    try:
        if action == 'pickup':
            contract.is_picked_up = True
            contract.pickup_datetime = datetime.now()
            if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
                messages.success(request, 'Contract marked as picked up.')
        elif action == 'return':
            contract.is_returned = True
            contract.return_datetime = datetime.now()
            if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
                messages.success(request, 'Contract marked as returned.')
            try:
                backfill_missing_returns(contract.trailer, contract.start_datetime)
            except Exception as e:
                logger.warning(f"Backfill returns failed for contract {pk}: {str(e)}")
        elif action == 'billed':
            contract.is_billed = True
            if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
                messages.success(request, 'Contract marked as billed.')
        elif action == 'invoiced':
            contract.is_invoiced = True
            if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
                messages.success(request, 'Contract marked as invoiced.')
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)
            
        contract.save()
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def get_available_trailers(request):
    """API endpoint to get available trailers for a category within a date range"""
    from rental_scheduler.services.availability import get_available_trailers_for_period
    
    category_id = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    current_contract_id = request.GET.get('current_contract_id')
    
    if not category_id:
        return JsonResponse({'error': 'Category ID is required'}, status=400)
        
    try:
        # Parse dates if provided
        start_datetime = None
        end_datetime = None
        
        if start_date and end_date:
            try:
                start_datetime = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
                end_datetime = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
                
                # Make datetimes timezone-aware
                if timezone.is_naive(start_datetime):
                    start_datetime = timezone.make_aware(start_datetime)
                if timezone.is_naive(end_datetime):
                    end_datetime = timezone.make_aware(end_datetime)
                    
            except ValueError as e:
                logger.error(f"Invalid date format: {str(e)}")
                return JsonResponse({'error': f'Invalid date format: {str(e)}'}, status=400)
        
        # Use the centralized availability logic
        available_trailers_query = get_available_trailers_for_period(
            category_id=category_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            exclude_contract_id=current_contract_id
        ).select_related('category')
        
        # In edit mode, ensure current trailer is included if it's in the right category
        if current_contract_id and start_datetime and end_datetime:
            try:
                contract = Contract.objects.select_related('trailer').get(id=current_contract_id)
                current_trailer = contract.trailer
                if current_trailer.category_id == int(category_id):
                    # Get list of available trailer IDs first to avoid circular reference
                    available_trailer_ids = list(available_trailers_query.values_list('id', flat=True))
                    # Include current trailer by combining available trailers with current trailer
                    all_trailers_in_category = Trailer.objects.filter(
                        category_id=category_id,
                        is_available=True
                    ).select_related('category')
                    
                    available_trailers_query = all_trailers_in_category.filter(
                        models.Q(id__in=available_trailer_ids) |
                        models.Q(id=current_trailer.id)
                    ).distinct()
            except Contract.DoesNotExist:
                pass
        
        # Sort by category, then size (length first, then width)
        trailers = list(available_trailers_query)
        trailers.sort(key=lambda t: (
            t.category.category.lower(),  # Category name (case-insensitive)
            float(t.length or 0),         # Length in feet
            float(t.width or 0)           # Width in feet
        ))
        
        # Build response data
        available_trailers = [{
            'id': trailer.id,
            'number': trailer.number,
            'size': f"{float(trailer.length):g}'x{float(trailer.width):g}'" if trailer.width and trailer.length else '',
            'width': float(trailer.width) if trailer.width else None,
            'length': float(trailer.length) if trailer.length else None,
            'model': trailer.model,
            'hauling_capacity': float(trailer.hauling_capacity) if trailer.hauling_capacity else None,
            'half_day_rate': float(trailer.half_day_rate),
            'daily_rate': float(trailer.daily_rate),
            'weekly_rate': float(trailer.weekly_rate)
        } for trailer in trailers]
        
        return JsonResponse({'trailers': available_trailers})
            
    except Exception as e:
        logger.error(f"Error in get_available_trailers: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

class CalendarView(TemplateView):
    template_name = 'rental_scheduler/calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Rental Calendar'
        context['categories'] = TrailerCategory.objects.all().order_by('category')
        
        # Sort trailers by category, then size (length first, then width)
        trailers = list(Trailer.objects.filter(is_available=True).select_related('category'))
        trailers.sort(key=lambda t: (
            t.category.category.lower(),  # Category name (case-insensitive)
            float(t.length or 0),         # Length in feet
            float(t.width or 0)           # Width in feet
        ))
        context['trailers'] = trailers
        
        return context

class AvailabilityView(TemplateView):
    template_name = 'rental_scheduler/availability.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Trailer Availability'
        context['categories'] = TrailerCategory.objects.all().order_by('category')
        
        # Add system settings for frontend calculations
        try:
            settings = SystemSettings.objects.first()
            if settings:
                context['tax_rate'] = settings.tax_rate
                context['winch_price'] = settings.winch_price
                context['hitch_bar_price'] = settings.hitch_bar_price
                context['furniture_blanket_price'] = settings.furniture_blanket_price
                context['strap_chain_price'] = settings.strap_chain_price
                context['evening_pickup_price'] = settings.evening_pickup_price
            else:
                context['tax_rate'] = 0
                context['winch_price'] = 0
                context['hitch_bar_price'] = 0
                context['furniture_blanket_price'] = 0
                context['strap_chain_price'] = 0
                context['evening_pickup_price'] = 0
        except:
            context['tax_rate'] = 0
            context['winch_price'] = 0
            context['hitch_bar_price'] = 0
            context['furniture_blanket_price'] = 0
            context['strap_chain_price'] = 0
            context['evening_pickup_price'] = 0
            
        return context

@require_http_methods(["GET"])
def get_calendar_data(request):
    """API endpoint to get calendar data for contracts and service periods"""
    try:
        # Get filter parameters
        category_id = request.GET.get('category')
        trailer_id = request.GET.get('trailer')
        
        # Base queryset for contracts
        contracts = Contract.objects.select_related(
            'customer', 'trailer', 'category'
        ).filter(show_in_calendar=True)
        
        # Apply filters
        if category_id:
            contracts = contracts.filter(category_id=category_id)
        if trailer_id:
            contracts = contracts.filter(trailer_id=trailer_id)
            
        # Base queryset for service periods
        services = TrailerService.objects.select_related('trailer', 'trailer__category')
        
        # Apply filters to services
        if category_id:
            services = services.filter(trailer__category_id=category_id)
        if trailer_id:
            services = services.filter(trailer_id=trailer_id)
            
        # Format events for FullCalendar
        events = []
        # Status colors - matches CSS variables and JavaScript config
        STATUS_COLORS = {
            'returned': '#3B82F6',   # blue-500
            'picked_up': '#16A34A',  # green-600 (changed from green-500 for better contrast)
            'pending': '#B45309',    # amber-700
            'service': '#DC2626',    # red-600 for service periods
            'overdue': '#C026D3',    # fuchsia-600 for overdue
        }

        # Add contract events
        for contract in contracts:
            now = timezone.now()
            is_overdue = (not contract.is_returned) and (now > contract.end_datetime)

            # Determine event color based on status using centralized colors
            if contract.is_returned:
                color = STATUS_COLORS['returned']
            elif contract.is_picked_up:
                color = STATUS_COLORS['picked_up']
            else:
                color = STATUS_COLORS['pending']
                
            # Create tooltip with additional information
            tooltip = f"""
            Customer: {contract.customer.name}
            Phone: {contract.customer.phone}
            Trailer: {contract.trailer.number} - {contract.trailer.model}
            Winch: {'Yes' if contract.includes_winch else 'No'}
            """
            
            # Only include phone number and icon if one exists
            phone_display = f"\n📞 {contract.customer.phone}" if contract.customer.phone else ""
            
            # Base event end is truncated to return time when returned
            base_end = contract.return_datetime.isoformat() if contract.is_returned and contract.return_datetime else contract.end_datetime.isoformat()

            event = {
                'id': f"contract-{contract.id}",
                'title': f"{contract.trailer.number} - {contract.customer.name}{phone_display}\n {' - Winch' if contract.includes_winch else ''}",
                'start': contract.start_datetime.isoformat(),
                'end': base_end,
                'backgroundColor': color,
                'borderColor': color,
                'extendedProps': {
                    'type': 'contract',
                    'contract_id': contract.id,
                    'tooltip': tooltip,
                    'is_picked_up': contract.is_picked_up,
                    'is_returned': contract.is_returned,
                    'is_overdue': False,
                    'is_billed': contract.is_billed,
                    'is_invoiced': contract.is_invoiced,
                    'includes_winch': contract.includes_winch,
                    'customer_name': contract.customer.name,
                    'customer_phone': contract.customer.phone,
                    'trailer_number': contract.trailer.number,
                    'trailer_model': contract.trailer.model,
                    'pickup_datetime': contract.pickup_datetime.isoformat() if contract.pickup_datetime else None,
                    'return_datetime': contract.return_datetime.isoformat() if contract.return_datetime else None,
                    'drivers_license_scanned': contract.customer.drivers_license_scanned
                }
            }
            events.append(event)

            # Add synthetic overdue segment from scheduled end to now
            if is_overdue:
                overdue_event = {
                    'id': f"contract-{contract.id}-overdue",
                    'title': f"{contract.trailer.number} - {contract.customer.name}{phone_display}",
                    'start': contract.end_datetime.isoformat(),
                    'end': now.isoformat(),
                    'backgroundColor': STATUS_COLORS['overdue'],
                    'borderColor': STATUS_COLORS['overdue'],
                    'extendedProps': {
                        'type': 'contract',
                        'contract_id': contract.id,
                        'tooltip': tooltip,
                        'is_picked_up': contract.is_picked_up,
                        'is_returned': False,
                        'is_overdue': True,
                        'is_billed': contract.is_billed,
                        'is_invoiced': contract.is_invoiced,
                        'includes_winch': contract.includes_winch,
                        'customer_name': contract.customer.name,
                        'customer_phone': contract.customer.phone,
                        'trailer_number': contract.trailer.number,
                        'trailer_model': contract.trailer.model,
                        'pickup_datetime': contract.pickup_datetime.isoformat() if contract.pickup_datetime else None,
                        'return_datetime': None,
                        'drivers_license_scanned': contract.customer.drivers_license_scanned
                    }
                }
                events.append(overdue_event)
        
        # Add service events
        for service in services:
            color = STATUS_COLORS['service']
            
            # Create tooltip for service
            tooltip = f"""
            Service: {service.trailer.number} - {service.trailer.model}
            Description: {service.description or 'No description'}
            Start: {service.start_datetime.strftime('%m/%d/%Y %I:%M %p')}
            End: {service.end_datetime.strftime('%m/%d/%Y %I:%M %p')}
            """
            
            description_display = f" - {service.description}" if service.description else ""
            
            event = {
                'id': f"service-{service.id}",
                'title': f"🔧 Service: {service.trailer.number}{description_display}",
                'start': service.start_datetime.isoformat(),
                'end': service.end_datetime.isoformat(),
                'backgroundColor': color,
                'borderColor': color,
                'extendedProps': {
                    'type': 'service',
                    'service_id': service.id,
                    'tooltip': tooltip,
                    'is_service': True,
                    'trailer_number': service.trailer.number,
                    'trailer_model': service.trailer.model,
                    'description': service.description or '',
                    'is_active': service.is_active,
                    'is_future': service.is_future,
                    'is_past': service.is_past
                }
            }
            events.append(event)
            
        return JsonResponse({
            'events': events,
            'status': 'success'
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)

class ContractPDFView(DetailView):
    model = Contract
    template_name = 'rental_scheduler/contract_pdf.html'
    
    def get(self, request, *args, **kwargs):
        try:
            logger.info("Starting PDF generation")
            contract = self.get_object()
            logger.info(f"Retrieved contract: {contract.id}")
            html_string = render_to_string(
                self.template_name,
                {
                    'contract': contract,
                    'now': timezone.now()
                }
            )
            css_path = os.path.join(settings.BASE_DIR, 'rental_scheduler', 'static', 'rental_scheduler', 'css', 'contract_pdf.min.css')
            pdf_content = HTML(string=html_string).write_pdf(stylesheets=[CSS(filename=css_path)])
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="contract_{contract.id}.pdf"'
            return response
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise

@require_http_methods(["PUT"])
def contract_status_toggle(request, pk):
    """
    API endpoint to toggle individual contract status flags via HTMX.
    Handles PUT requests with checkbox form data for status updates.
    """
    try:
        contract = get_object_or_404(Contract, pk=pk)
        
        # Parse the form data from the PUT request
        if request.content_type == 'application/x-www-form-urlencoded':
            # Parse the body for form data
            form_data = {}
            body = request.body.decode('utf-8')
            for pair in body.split('&'):
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    # URL decode the key and value
                    import urllib.parse
                    key = urllib.parse.unquote_plus(key)
                    value = urllib.parse.unquote_plus(value)
                    form_data[key] = value
        else:
            form_data = {}
        
        # Define the boolean fields that can be toggled
        toggleable_fields = {
            'is_billed': 'is_billed',
            'is_invoiced': 'is_invoiced', 
            'is_picked_up': 'is_picked_up',
            'is_returned': 'is_returned'
        }
        
        # Track what changed for logging
        changes = {}
        
        # Update fields based on checkbox presence
        for field_name, model_field in toggleable_fields.items():
            # Checkbox is checked if field name is present in form data
            new_value = field_name in form_data
            old_value = getattr(contract, model_field)
            
            if new_value != old_value:
                setattr(contract, model_field, new_value)
                changes[field_name] = {'from': old_value, 'to': new_value}
                
                # Handle special cases for datetime fields
                if field_name == 'is_picked_up' and new_value:
                    contract.pickup_datetime = timezone.now()
                elif field_name == 'is_returned' and new_value:
                    # Use provided return_datetime or default to now
                    return_datetime_str = form_data.get('return_datetime')
                    if return_datetime_str:
                        try:
                            # Parse the datetime-local format from the form
                            return_datetime = datetime.strptime(return_datetime_str, '%Y-%m-%dT%H:%M')
                            # Make it timezone-aware
                            contract.return_datetime = timezone.make_aware(return_datetime)
                            changes['return_datetime'] = {'from': contract.return_datetime, 'to': return_datetime_str}
                        except ValueError as e:
                            logger.warning(f"Invalid return_datetime format: {return_datetime_str}, using current time")
                            contract.return_datetime = timezone.now()
                    else:
                        contract.return_datetime = timezone.now()
                elif field_name == 'is_returned' and not new_value:
                    contract.return_datetime = None
                    changes['return_datetime'] = {'from': contract.return_datetime, 'to': None}
        
        # If return_datetime was provided but is_returned state didn't change, update it explicitly
        if 'return_datetime' in form_data and 'is_returned' not in changes:
            try:
                rd = datetime.strptime(form_data['return_datetime'], '%Y-%m-%dT%H:%M')
                if timezone.is_naive(rd):
                    rd = timezone.make_aware(rd)
                if contract.return_datetime != rd:
                    changes['return_datetime'] = {
                        'from': contract.return_datetime.isoformat() if contract.return_datetime else None,
                        'to': rd.isoformat()
                    }
                    contract.return_datetime = rd
                    # Ensure flag consistency
                    if not contract.is_returned:
                        contract.is_returned = True
                        changes['is_returned'] = {'from': False, 'to': True}
            except Exception as e:
                logger.warning(f"contract_status_toggle: invalid return_datetime '{form_data.get('return_datetime')}' - {e}")

        if changes:
            contract.save()
            logger.info(f"Contract {pk} status updated via HTMX: {changes}")
            if 'is_returned' in changes and changes['is_returned'].get('to') is True:
                try:
                    backfill_missing_returns(contract.trailer, contract.start_datetime)
                except Exception as e:
                    logger.warning(f"Backfill returns failed for contract {pk}: {str(e)}")
        
        # Return JSON response with current status for frontend updates
        response_data = {
            'id': contract.id,
            'is_billed': contract.is_billed,
            'is_invoiced': contract.is_invoiced,
            'is_picked_up': contract.is_picked_up,
            'is_returned': contract.is_returned,
            'pickup_datetime': contract.pickup_datetime.isoformat() if contract.pickup_datetime else None,
            'return_datetime': contract.return_datetime.isoformat() if contract.return_datetime else None,
            'status': 'success',
            'changes': changes
        }
        
        return JsonResponse(response_data)
        
    except Contract.DoesNotExist:
        logger.warning(f"Contract {pk} not found for status toggle")
        return JsonResponse({
            'error': 'Contract not found',
            'status': 'error'
        }, status=404)
        
    except Exception as e:
        logger.error(f"Error toggling contract {pk} status: {str(e)}")
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)

def test_404(request):
    """Test view to demonstrate 404 error page"""
    from django.http import Http404
    raise Http404("This is a test 404 error page")

def test_500(request):
    """Test view to demonstrate 500 error page"""
    raise Exception("This is a test 500 error page")

def test_403(request):
    """Test view to demonstrate 403 error page"""
    from django.core.exceptions import PermissionDenied
    raise PermissionDenied("This is a test 403 error page")

def test_400(request):
    """Test view to demonstrate 400 error page"""
    from django.core.exceptions import BadRequest
    raise BadRequest("This is a test 400 error page")

@require_http_methods(["GET"])
def test_network_connection(request):
    """API endpoint to test network connection with credentials."""
    
    try:
        path = request.GET.get('path')
        username = request.GET.get('username')
        password = request.GET.get('password')
        
        if not path:
            return JsonResponse({'error': 'Path is required'}, status=400)
            
        # Use empty string instead of None for missing credentials
        username = username or ''
        password = password or ''
        
        # Only use credentials if both are provided
        use_credentials = bool(username and password)
        
        logger.info(f"Testing connection to {path}" + (" with credentials" if use_credentials else ""))
        
        success = connect_to_network_share(
            path, 
            username=username if use_credentials else None,
            password=password if use_credentials else None
        )
        
        if success:
            logger.info(f"Connection to {path} successful")
            return JsonResponse({'success': True})
        else:
            logger.warning(f"Connection to {path} failed")
            return JsonResponse({
                'success': False,
                'error': 'Could not connect to network path'
            })
            
    except Exception as e:
        logger.error(f"Error testing network connection: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

class TrailerServiceManagementView(TemplateView):
    template_name = 'rental_scheduler/service_management.html'
    
    def get_object_trailer(self):
        """Get the trailer this service management is for"""
        return get_object_or_404(Trailer, pk=self.kwargs['trailer_pk'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trailer = self.get_object_trailer()
        
        # Get all services for this trailer, ordered by start date
        all_services = trailer.trailerservice_set.all().order_by('start_datetime')
        
        context.update({
            'title': f'Service Management - {trailer.number}',
            'trailer': trailer,
            'all_services': all_services,
            'active_services': trailer.active_services,
            'upcoming_services': trailer.upcoming_services, 
            'completed_services': trailer.completed_services,
            'back_url': reverse_lazy('rental_scheduler:trailer_list'),
        })
        
        return context

@require_http_methods(["GET"])
def availability_search(request):
    """API endpoint to get both available and unavailable trailers for a category within a date range"""
    from rental_scheduler.services.availability import get_available_trailers_for_period, is_trailer_available
    from rental_scheduler.services.rental_calculator import RentalCalculator
    from rental_scheduler.models import TrailerService
    from django.template.loader import render_to_string
    from django.db.models import Q
    
    category_id = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    search_term = request.GET.get('search', '').strip()
    
    if not category_id:
        return JsonResponse({'error': 'Category ID is required'}, status=400)
    
    if not start_date or not end_date:
        return JsonResponse({'error': 'Start and end dates are required'}, status=400)
    
    def apply_search_filter(queryset, search_term):
        """Apply search logic for number and size"""
        if not search_term:
            return queryset
            
        # Search in trailer number (case-insensitive partial match)
        number_q = Q(number__icontains=search_term)
        
        # Initialize size query
        size_q = Q()
        
        # Handle dimension searches with 'x' (like "16x", "12x6", "16x8")
        if 'x' in search_term.lower():
            try:
                parts = search_term.lower().replace(' ', '').split('x')
                if len(parts) == 2:
                    length_str, width_str = parts
                    
                    # Handle complete dimension searches like "16x8"
                    if length_str and width_str:
                        try:
                            length_val = float(length_str)
                            width_val = float(width_str)
                            size_q |= Q(length=length_val, width=width_val)
                        except ValueError:
                            pass
                    
                    # Handle partial dimension searches like "16x" (any width)
                    elif length_str and not width_str:
                        try:
                            length_val = float(length_str)
                            size_q |= Q(length=length_val)
                        except ValueError:
                            pass
                    
                    # Handle partial dimension searches like "x8" (any length)
                    elif not length_str and width_str:
                        try:
                            width_val = float(width_str)
                            size_q |= Q(width=width_val)
                        except ValueError:
                            pass
            except:
                pass
        else:
            # For non-'x' searches, try to match individual dimensions
            try:
                dimension_val = float(search_term)
                size_q = Q(length=dimension_val) | Q(width=dimension_val)
            except ValueError:
                pass
        
        # Search in model name as well
        model_q = Q(model__icontains=search_term)
        
        # Combine all search conditions
        return queryset.filter(number_q | size_q | model_q)
        
    try:
        # Parse dates
        start_datetime = None
        end_datetime = None
        
        try:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
            
            # Make timezone-aware
            if timezone.is_naive(start_datetime):
                start_datetime = timezone.make_aware(start_datetime)
            if timezone.is_naive(end_datetime):
                end_datetime = timezone.make_aware(end_datetime)
                
        except ValueError as e:
            logger.error(f"Invalid date format: {str(e)}")
            return JsonResponse({'error': f'Invalid date format: {str(e)}'}, status=400)
        
        # Validate dates
        if end_datetime <= start_datetime:
            return JsonResponse({'error': 'End date must be after start date'}, status=400)
        
        # Get system settings for pricing
        settings = SystemSettings.objects.first()
        tax_rate = Decimal(str(settings.tax_rate if settings else 0))
        
        # Get all trailers in the category, sorted by size
        all_trailers_in_category = Trailer.objects.filter(
            category_id=category_id,
            is_available=True
        ).select_related('category').order_by('length', 'width', 'number')
        
        # Apply search filter to all trailers
        all_trailers_in_category = apply_search_filter(all_trailers_in_category, search_term)
        
        # Calculate duration once for all trailers (since it's the same for all)
        duration_info = RentalCalculator.calculate_duration_info(start_datetime, end_datetime)
        duration_display = RentalCalculator.format_duration_display(duration_info)
        rate_category = duration_info['rate_category'].replace('_', ' ').title()
        has_half_day = duration_info.get('has_half_day', False)
        
        # Get available trailers, sorted by size
        available_trailers_query = get_available_trailers_for_period(
            category_id=category_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime
        ).select_related('category').order_by('length', 'width', 'number')
        
        # Apply search filter to available trailers
        available_trailers_query = apply_search_filter(available_trailers_query, search_term)
        
        available_trailers = []
        for trailer in available_trailers_query:
            try:
                # Calculate pricing using the already calculated duration
                base_rate = RentalCalculator.calculate_base_rate(trailer, duration_info['days'])
                
                # Calculate the unit rate based on rate category (like in contract form)
                rate_category = duration_info['rate_category']
                if rate_category == 'half_day':
                    unit_rate = trailer.half_day_rate
                elif rate_category == 'daily':
                    unit_rate = trailer.daily_rate
                elif rate_category == 'weekly':
                    unit_rate = trailer.weekly_rate
                elif rate_category == 'extended':
                    unit_rate = trailer.weekly_rate / 6  # Extended daily rate
                else:
                    unit_rate = base_rate  # Fallback to calculated rate
                
                # Calculate totals (no add-ons for availability display)
                totals = RentalCalculator.calculate_totals(
                    base_rate=base_rate,
                    addon_costs=Decimal('0'),
                    extra_mileage=Decimal('0'),
                    tax_rate=tax_rate,
                    down_payment=Decimal('0')
                )
                
                available_trailers.append({
                    'id': trailer.id,
                    'number': trailer.number,
                    'model': trailer.model,
                    'size': f"{float(trailer.length):g}'x{float(trailer.width):g}'" if trailer.width and trailer.length else '',
                    'hauling_capacity': float(trailer.hauling_capacity) if trailer.hauling_capacity else None,
                    'unit_rate': float(unit_rate),  # Unit rate for display
                    'base_rate': float(base_rate),  # Total calculated rate
                    'half_day_rate': float(trailer.half_day_rate),  # Half-day rate for display
                    'tax_amount': float(totals['tax_amount']),
                    'total': float(totals['total_amount'])
                })
            except Exception as e:
                logger.error(f"Error calculating pricing for trailer {trailer.id}: {str(e)}")
                continue
        
        # Get unavailable trailers and reasons
        available_trailer_ids = [t['id'] for t in available_trailers]
        unavailable_trailers = []
        
        for trailer in all_trailers_in_category:
            if trailer.id not in available_trailer_ids:
                # Determine why it's unavailable
                is_available, reason = is_trailer_available(trailer, start_datetime, end_datetime)
                
                trailer_info = {
                    'id': trailer.id,
                    'number': trailer.number,
                    'model': trailer.model,
                    'size': f"{float(trailer.length):g}'x{float(trailer.width):g}'" if trailer.width and trailer.length else '',
                    'hauling_capacity': float(trailer.hauling_capacity) if trailer.hauling_capacity else None,
                    'reason': reason,
                    'details': []
                }
                
                # Get specific details for each reason
                if reason == 'booked':
                    returned_overlap = Contract.objects.filter(
                        trailer=trailer,
                        is_returned=True,
                        start_datetime__lt=end_datetime,
                        return_datetime__gt=start_datetime
                    ).select_related('customer')

                    not_returned_overlap = Contract.objects.filter(
                        trailer=trailer,
                        is_returned=False,
                        start_datetime__lt=end_datetime
                    ).select_related('customer')

                    has_overdue = False
                    for contract in returned_overlap:
                        is_late = contract.return_datetime and contract.return_datetime > contract.end_datetime
                        if is_late:
                            has_overdue = True
                        trailer_info['details'].append({
                            'id': contract.id,
                            'type': 'contract',
                            'status': 'returned_late' if is_late else 'returned_early',
                            'start': format_local(contract.start_datetime),
                            'scheduled_end': format_local(contract.end_datetime),
                            'end': format_local(contract.return_datetime) if contract.return_datetime else None,
                            'return_iso': to_local(contract.return_datetime).isoformat() if contract.return_datetime else None,
                            'customer': contract.customer.name,
                            'is_picked_up': contract.is_picked_up,
                            'is_returned': contract.is_returned,
                            'is_invoiced': contract.is_invoiced
                        })

                    now_dt = timezone.now()
                    for contract in not_returned_overlap:
                        is_past_due = contract.end_datetime <= now_dt
                        if is_past_due:
                            has_overdue = True
                        trailer_info['details'].append({
                            'id': contract.id,
                            'type': 'contract',
                            'status': 'not_returned',
                            'start': format_local(contract.start_datetime),
                            'scheduled_end': format_local(contract.end_datetime),
                            'is_past_due': is_past_due,
                            'return_iso': to_local(contract.return_datetime).isoformat() if contract.return_datetime else None,
                            'customer': contract.customer.name,
                            'is_picked_up': contract.is_picked_up,
                            'is_returned': contract.is_returned,
                            'is_invoiced': contract.is_invoiced
                        })
                    trailer_info['has_overdue'] = has_overdue

                    # If no overlaps actually block, skip adding to unavailable
                    if not returned_overlap.exists() and not not_returned_overlap.exists():
                        continue
                
                elif reason == 'under_service':
                    # Get overlapping services
                    overlapping_services = TrailerService.objects.filter(
                        trailer=trailer,
                        start_datetime__lt=end_datetime,
                        end_datetime__gt=start_datetime
                    )
                    
                    for service in overlapping_services:
                        trailer_info['details'].append({
                            'type': 'service',
                            'start': format_local(service.start_datetime),
                            'end': format_local(service.end_datetime),
                            'description': getattr(service, 'description', None) or 'Service'
                        })
                
                elif reason == 'not_active':
                    trailer_info['details'].append({
                        'type': 'inactive',
                        'message': 'Trailer is marked as not available'
                    })
                
                # Only append if there are real blocking details or reason is not service/booked
                if trailer_info['reason'] != 'booked' or trailer_info['details']:
                    unavailable_trailers.append(trailer_info)
        
        # Render partial templates
        available_html = render_to_string(
            'rental_scheduler/partials/availability_results.html',
            {
                'available_trailers': available_trailers,
                'start_datetime': start_datetime,
                'end_datetime': end_datetime,
                'category_id': category_id,
                'duration_display': duration_display,
                'rate_category': rate_category,
                'has_half_day': has_half_day
            },
            request=request
        )
        
        unavailable_html = render_to_string(
            'rental_scheduler/partials/unavailability_results.html',
            {
                'unavailable_trailers': unavailable_trailers
            },
            request=request
        )
        
        return JsonResponse({
            'success': True,
            'available_html': available_html,
            'unavailable_html': unavailable_html,
            'available_count': len(available_trailers),
            'unavailable_count': len(unavailable_trailers),
            'duration_display': duration_display,
            'rate_category': rate_category
        })
            
    except Exception as e:
        logger.error(f"Error in availability_search: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
