from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Job


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