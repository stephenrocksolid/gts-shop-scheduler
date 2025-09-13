from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Job, WorkOrder, WorkOrderLine


class JobForm(forms.ModelForm):
    """Form for editing job details with validation"""
    
    class Meta:
        model = Job
        fields = [
            'business_name', 'contact_name', 'phone',
            'address_line1', 'address_line2', 'city', 'state', 'postal_code',
            'start_dt', 'end_dt', 'all_day',
            'trailer_color', 'trailer_serial', 'trailer_details',
            'notes', 'repair_notes', 'quote', 'status'
        ]
        widgets = {
            'business_name': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-1 focus:ring-blue-500',
                'placeholder': 'Enter business name'
            }),
            'contact_name': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-1 focus:ring-blue-500',
                'placeholder': 'Enter contact name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-1 focus:ring-blue-500',
                'type': 'tel',
                'placeholder': '(555) 123-4567'
            }),
            'address_line1': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-1 focus:ring-blue-500',
                'placeholder': 'Street address'
            }),
            'address_line2': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-1 focus:ring-blue-500',
                'placeholder': 'Apt, suite, etc.'
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-1 focus:ring-blue-500',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-1 focus:ring-blue-500',
                'placeholder': 'State',
                'maxlength': '2'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-1 focus:ring-blue-500',
                'placeholder': 'ZIP code'
            }),
            'start_dt': forms.DateTimeInput(attrs={
                'class': 'w-full rounded-xl border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-1 focus:ring-blue-500',
                'type': 'datetime-local'
            }),
            'end_dt': forms.DateTimeInput(attrs={
                'class': 'w-full rounded-xl border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-1 focus:ring-blue-500',
                'type': 'datetime-local'
            }),
            'all_day': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-blue-600 focus:ring-blue-500',
                'onchange': 'toggleTimeInputs(this)'
            }),
            'trailer_color': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-1 focus:ring-blue-500',
                'placeholder': 'Trailer color'
            }),
            'trailer_serial': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-1 focus:ring-blue-500',
                'placeholder': 'Serial number'
            }),
            'trailer_details': forms.Textarea(attrs={
                'class': 'w-full rounded-xl border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-1 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Additional trailer details'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full rounded-xl border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-1 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'General job notes'
            }),
            'repair_notes': forms.Textarea(attrs={
                'class': 'w-full rounded-xl border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-1 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Detailed repair notes'
            }),
            'quote': forms.NumberInput(attrs={
                'class': 'w-full rounded-xl border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-1 focus:ring-blue-500',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full rounded-xl border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-1 focus:ring-blue-500'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make business_name required
        self.fields['business_name'].required = True
        self.fields['start_dt'].required = True
        self.fields['end_dt'].required = True
        
        # Add required asterisks to labels
        required_fields = ['business_name', 'start_dt', 'end_dt']
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].label = f"{self.fields[field_name].label} *"
    
    def clean_phone(self):
        """Clean and format phone number"""
        phone = self.cleaned_data.get('phone', '')
        if phone:
            # Remove all non-digit characters
            phone_digits = ''.join(filter(str.isdigit, phone))
            if len(phone_digits) == 10:
                # Format as (XXX) XXX-XXXX
                return f"({phone_digits[:3]}) {phone_digits[3:6]}-{phone_digits[6:]}"
            elif len(phone_digits) == 11 and phone_digits[0] == '1':
                # Format as 1 (XXX) XXX-XXXX
                return f"1 ({phone_digits[1:4]}) {phone_digits[4:7]}-{phone_digits[7:]}"
        return phone
    
    def clean(self):
        """Validate the form data"""
        cleaned_data = super().clean()
        start_dt = cleaned_data.get('start_dt')
        end_dt = cleaned_data.get('end_dt')
        all_day = cleaned_data.get('all_day', False)
        
        # If all_day is checked, clear specific times
        if all_day and start_dt and end_dt:
            # Set start time to midnight
            start_dt = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
            # Set end time to 23:59:59
            end_dt = end_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
            cleaned_data['start_dt'] = start_dt
            cleaned_data['end_dt'] = end_dt
        
        # Validate that end date is after start date
        if start_dt and end_dt:
            if start_dt >= end_dt:
                raise ValidationError({
                    'end_dt': 'End date must be after start date'
                })
        
        return cleaned_data


class WorkOrderForm(forms.ModelForm):
    """Form for creating and editing work orders"""
    
    class Meta:
        model = WorkOrder
        fields = ['job', 'wo_number', 'wo_date', 'notes']
        widgets = {
            'job': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'wo_number': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'e.g., WO-2024-001'
            }),
            'wo_date': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 4,
                'placeholder': 'Additional notes about the work order...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show jobs that don't already have work orders
        if not self.instance.pk:  # Creating new work order
            self.fields['job'].queryset = Job.objects.filter(
                is_deleted=False,
                work_order__isnull=True
            )
        else:  # Editing existing work order
            self.fields['job'].queryset = Job.objects.filter(is_deleted=False)
    
    def clean_wo_number(self):
        wo_number = self.cleaned_data.get('wo_number')
        if wo_number:
            # Check for duplicates, excluding current instance
            queryset = WorkOrder.objects.filter(wo_number=wo_number)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise ValidationError('A work order with this number already exists.')
        return wo_number


class WorkOrderLineForm(forms.ModelForm):
    """Form for creating and editing work order line items"""
    
    class Meta:
        model = WorkOrderLine
        fields = ['item_code', 'description', 'qty', 'rate']
        widgets = {
            'item_code': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Part #'
            }),
            'description': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Description of work or item'
            }),
            'qty': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'step': '0.01',
                'min': '0'
            }),
            'rate': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'step': '0.01',
                'min': '0'
            })
        }
    
    def clean_qty(self):
        qty = self.cleaned_data.get('qty')
        if qty is not None and qty < 0:
            raise ValidationError('Quantity cannot be negative.')
        return qty
    
    def clean_rate(self):
        rate = self.cleaned_data.get('rate')
        if rate is not None and rate < 0:
            raise ValidationError('Rate cannot be negative.')
        return rate
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Calculate total
        if instance.qty is not None and instance.rate is not None:
            instance.total = instance.qty * instance.rate
        if commit:
            instance.save()
        return instance