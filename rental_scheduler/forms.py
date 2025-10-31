from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Job, WorkOrder, WorkOrderLine, Calendar, CallReminder


class JobForm(forms.ModelForm):
    """Form for editing job details with validation"""
    
    # Override date fields to accept both datetime-local and date-only formats
    start_dt = forms.DateTimeField(
        required=True,
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d'],  # datetime-local and date-only
        widget=forms.DateTimeInput(attrs={
            'class': 'w-full rounded-xl border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-1 focus:ring-blue-500',
            'type': 'datetime-local'
        })
    )
    
    end_dt = forms.DateTimeField(
        required=True,
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d'],  # datetime-local and date-only
        widget=forms.DateTimeInput(attrs={
            'class': 'w-full rounded-xl border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-1 focus:ring-blue-500',
            'type': 'datetime-local'
        })
    )
    
    class Meta:
        model = Job
        fields = [
            'business_name', 'contact_name', 'phone',
            'address_line1', 'address_line2', 'city', 'state', 'postal_code',
            'start_dt', 'end_dt', 'all_day',
            'has_call_reminder', 'call_reminder_weeks_prior', 'call_reminder_completed',
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
        
        # If all_day is checked, normalize times to noon to avoid timezone shift issues
        if all_day and start_dt and end_dt:
            # Set both start and end time to noon
            start_dt = start_dt.replace(hour=12, minute=0, second=0, microsecond=0)
            end_dt = end_dt.replace(hour=12, minute=0, second=0, microsecond=0)
            cleaned_data['start_dt'] = start_dt
            cleaned_data['end_dt'] = end_dt
        
        # Validate that end date is after (or equal for all-day events) start date
        if start_dt and end_dt:
            # For all-day events, allow same day (start_dt == end_dt)
            if all_day:
                if start_dt > end_dt:
                    raise ValidationError({
                        'end_dt': 'End date cannot be before start date'
                    })
            else:
                # For timed events, end must be strictly after start
                if start_dt >= end_dt:
                    raise ValidationError({
                        'end_dt': 'End date/time must be after start date/time'
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


class CalendarImportForm(forms.Form):
    """Form for importing calendar events from .ics files"""
    
    ics_file = forms.FileField(
        label='ICS Calendar File',
        help_text='Upload a .ics (iCalendar) file exported from Mozilla Thunderbird or other calendar applications.',
        widget=forms.FileInput(attrs={
            'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none focus:border-blue-500',
            'accept': '.ics'
        })
    )
    
    calendar = forms.ModelChoiceField(
        queryset=Calendar.objects.filter(is_active=True),
        label='Import to Calendar',
        help_text='Select which calendar to import these events into.',
        widget=forms.Select(attrs={
            'class': 'w-full rounded-xl border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-1 focus:ring-blue-500'
        })
    )
    
    use_ai_parsing = forms.BooleanField(
        required=False,
        initial=True,
        label='Use AI to extract trailer details',
        help_text='AI will automatically extract trailer color, serial number, repair notes, and quote from descriptions. Small API cost per event (~$0.0001-0.0003).',
        widget=forms.CheckboxInput(attrs={
            'class': 'rounded border-gray-300 text-blue-600 focus:ring-blue-500'
        })
    )
    
    def clean_ics_file(self):
        """Validate the uploaded file"""
        ics_file = self.cleaned_data.get('ics_file')
        
        if ics_file:
            # Check file extension
            if not ics_file.name.endswith('.ics'):
                raise ValidationError('File must have a .ics extension.')
            
            # Check file size (limit to 10MB)
            if ics_file.size > 10 * 1024 * 1024:
                raise ValidationError('File size must be less than 10MB.')
        
        return ics_file


class JobImportForm(forms.Form):
    """Form for importing jobs from JSON export files"""
    
    json_file = forms.FileField(
        label='JSON Export File',
        help_text='Upload a .json file exported from this application.',
        widget=forms.FileInput(attrs={
            'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none focus:border-blue-500',
            'accept': '.json'
        })
    )
    
    target_calendar = forms.ModelChoiceField(
        queryset=Calendar.objects.filter(is_active=True),
        label='Import to Calendar',
        help_text='Select which calendar to import these jobs into. All imported jobs will be assigned to this calendar.',
        widget=forms.Select(attrs={
            'class': 'w-full rounded-xl border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-1 focus:ring-blue-500'
        })
    )
    
    def clean_json_file(self):
        """Validate the uploaded JSON file"""
        json_file = self.cleaned_data.get('json_file')
        
        if json_file:
            # Check file extension
            if not json_file.name.endswith('.json'):
                raise ValidationError('File must have a .json extension.')
            
            # Check file size (limit to 50MB)
            if json_file.size > 50 * 1024 * 1024:
                raise ValidationError('File size must be less than 50MB.')
            
            # Try to parse JSON to validate structure
            try:
                json_file.seek(0)
                content = json_file.read()
                json_file.seek(0)  # Reset for later reading
                
                import json
                data = json.loads(content)
                
                # Validate basic structure
                if not isinstance(data, dict):
                    raise ValidationError('Invalid JSON structure: root must be an object.')
                
                if 'version' not in data:
                    raise ValidationError('Invalid export file: missing version field.')
                
                if 'jobs' not in data:
                    raise ValidationError('Invalid export file: missing jobs array.')
                
                if not isinstance(data['jobs'], list):
                    raise ValidationError('Invalid export file: jobs must be an array.')
                
            except json.JSONDecodeError as e:
                raise ValidationError(f'Invalid JSON file: {str(e)}')
            except UnicodeDecodeError:
                raise ValidationError('File encoding error. Please ensure the file is UTF-8 encoded.')
        
        return json_file


class CallReminderForm(forms.ModelForm):
    """Form for creating and editing call reminders"""
    
    reminder_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none',
            'type': 'date'
        }),
        help_text='The Sunday this reminder will appear on'
    )
    
    class Meta:
        model = CallReminder
        fields = ['calendar', 'reminder_date', 'notes']
        widgets = {
            'calendar': forms.Select(attrs={
                'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none',
                'rows': 4,
                'placeholder': 'Enter notes about this call reminder...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['calendar'].queryset = Calendar.objects.filter(is_active=True)
        self.fields['notes'].required = False
    
    def clean_reminder_date(self):
        """Validate that the reminder date is a Sunday"""
        reminder_date = self.cleaned_data.get('reminder_date')
        if reminder_date:
            # Check if it's a Sunday (weekday() returns 6 for Sunday)
            # Temporarily disabled for debugging
            # if reminder_date.weekday() != 6:
            #     raise ValidationError('Reminder date must be a Sunday.')
            pass
        return reminder_date