from django.contrib import admin
from .models import Calendar, Customer, Trailer, Job, WorkOrder, WorkOrderLine, Invoice, InvoiceLine, StatusChange, PrintTemplateSetting

# Register your models here.

@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):
    """Admin configuration for Calendar model"""
    list_display = ['name', 'color', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'color', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        """Return all calendars ordered by name"""
        return super().get_queryset(request).order_by('name')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Admin configuration for Customer model"""
    list_display = ['display_name', 'primary_phone', 'email', 'city', 'state', 'created_at']
    list_filter = ['created_at', 'state', 'city']
    search_fields = ['business_name', 'contact_name', 'phone', 'alt_phone', 'email', 'address_line1', 'city']
    ordering = ['business_name', 'contact_name']
    
    fieldsets = (
        ('Business Information', {
            'fields': ('business_name', 'contact_name')
        }),
        ('Contact Information', {
            'fields': ('phone', 'alt_phone', 'email')
        }),
        ('Address Information', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'postal_code')
        }),
        ('Additional Information', {
            'fields': ('notes', 'po_number', 'drivers_license_number', 'drivers_license_scan', 'drivers_license_scanned')
        }),
        ('Legacy Fields', {
            'fields': ('name', 'street_address', 'zip_code'),
            'classes': ('collapse',),
            'description': 'Legacy fields for backward compatibility'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'drivers_license_scanned']
    
    def display_name(self, obj):
        """Display the customer name in the admin list"""
        return obj.display_name
    display_name.short_description = 'Customer Name'
    
    def primary_phone(self, obj):
        """Display the primary phone number in the admin list"""
        return obj.primary_phone
    primary_phone.short_description = 'Phone'
    
    def get_queryset(self, request):
        """Return customers ordered by business name and contact name"""
        return super().get_queryset(request).order_by('business_name', 'contact_name')

@admin.register(Trailer)
class TrailerAdmin(admin.ModelAdmin):
    """Admin configuration for Trailer model"""
    list_display = ['display_name', 'category', 'customer', 'color', 'is_available', 'is_rental_trailer', 'created_at']
    list_filter = ['category', 'is_available', 'is_rental_trailer', 'created_at', 'customer']
    search_fields = ['number', 'model', 'serial_number', 'color', 'description', 'customer__business_name', 'customer__contact_name']
    ordering = ['number']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('number', 'model', 'category', 'customer')
        }),
        ('Identification', {
            'fields': ('serial_number', 'color', 'description')
        }),
        ('Physical Specifications', {
            'fields': ('hauling_capacity', 'length', 'width', 'height')
        }),
        ('Rental Information', {
            'fields': ('is_rental_trailer', 'half_day_rate', 'daily_rate', 'weekly_rate')
        }),
        ('Status', {
            'fields': ('is_available', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def display_name(self, obj):
        """Display the trailer name in the admin list"""
        return obj.display_name
    display_name.short_description = 'Trailer'
    
    def get_queryset(self, request):
        """Return trailers ordered by number"""
        return super().get_queryset(request).order_by('number')


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    """Admin configuration for Job model"""
    list_display = ['display_name', 'trailer_info', 'calendar', 'status', 'start_dt', 'end_dt', 'is_overdue_display']
    list_filter = ['status', 'calendar', 'all_day', 'repeat_type', 'is_deleted', 'start_dt', 'created_at']
    search_fields = [
        'business_name', 'contact_name', 'phone', 'address_line1', 'city',
        'customer__business_name', 'customer__contact_name', 'customer__phone',
        'trailer__number', 'trailer__model', 'trailer__serial_number',
        'repair_notes', 'quote_text'
    ]
    ordering = ['-start_dt']
    date_hierarchy = 'start_dt'
    
    fieldsets = (
        ('Scheduling', {
            'fields': ('calendar', 'status', 'start_dt', 'end_dt', 'all_day')
        }),
        ('Customer Information', {
            'fields': ('customer', 'trailer')
        }),
        ('Contact Override', {
            'fields': ('business_name', 'contact_name', 'phone'),
            'description': 'Override customer contact information if different for this job'
        }),
        ('Address Override', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'postal_code'),
            'description': 'Override customer address if different for this job'
        }),
        ('Job Details', {
            'fields': ('date_call_received', 'repair_notes', 'quote_text')
        }),
        ('Repeat Settings', {
            'fields': ('repeat_type', 'repeat_n_months'),
            'description': 'Configure recurring job settings'
        }),
        ('Display Options', {
            'fields': ('trailer_color_overwrite',),
            'description': 'Override trailer color for calendar display'
        }),
        ('System Information', {
            'fields': ('is_deleted', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def display_name(self, obj):
        """Display the job name in the admin list"""
        return obj.display_name
    display_name.short_description = 'Customer'
    
    def trailer_info(self, obj):
        """Display trailer information in the admin list"""
        return f"{obj.trailer.number} - {obj.trailer.model}"
    trailer_info.short_description = 'Trailer'
    
    def is_overdue_display(self, obj):
        """Display overdue status in the admin list"""
        if obj.is_overdue:
            return "⚠️ OVERDUE"
        return ""
    is_overdue_display.short_description = 'Status'
    
    def get_queryset(self, request):
        """Return jobs ordered by start date (newest first)"""
        return super().get_queryset(request).select_related('customer', 'trailer', 'calendar')


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    """Admin configuration for WorkOrder model"""
    list_display = ['wo_number', 'job_info', 'wo_date', 'total_amount', 'line_count', 'created_at']
    list_filter = ['wo_date', 'created_at']
    search_fields = [
        'wo_number', 'job__display_name', 'job__customer__business_name',
        'job__customer__contact_name', 'job__trailer__number', 'notes'
    ]
    ordering = ['-wo_date', '-created_at']
    date_hierarchy = 'wo_date'
    
    fieldsets = (
        ('Work Order Information', {
            'fields': ('wo_number', 'wo_date', 'job')
        }),
        ('Details', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def job_info(self, obj):
        """Display job information in the admin list"""
        return f"{obj.job.display_name} - {obj.job.trailer.display_name}"
    job_info.short_description = 'Job'
    
    def total_amount(self, obj):
        """Display total amount in the admin list"""
        return f"${obj.total_amount:.2f}"
    total_amount.short_description = 'Total'
    
    def line_count(self, obj):
        """Display line count in the admin list"""
        return obj.line_count
    line_count.short_description = 'Lines'
    
    def get_queryset(self, request):
        """Return work orders with related data"""
        return super().get_queryset(request).select_related('job__customer', 'job__trailer')


@admin.register(WorkOrderLine)
class WorkOrderLineAdmin(admin.ModelAdmin):
    """Admin configuration for WorkOrderLine model"""
    list_display = ['work_order', 'item_code', 'description', 'qty', 'rate', 'total', 'created_at']
    list_filter = ['created_at', 'work_order__wo_date']
    search_fields = [
        'item_code', 'description', 'work_order__wo_number',
        'work_order__job__display_name'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        ('Line Information', {
            'fields': ('work_order', 'item_code', 'description')
        }),
        ('Pricing', {
            'fields': ('qty', 'rate', 'total')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        """Return work order lines with related data"""
        return super().get_queryset(request).select_related('work_order__job__customer', 'work_order__job__trailer')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Admin configuration for Invoice model"""
    list_display = ['invoice_number', 'job_info', 'invoice_date', 'bill_to_display_name', 'total_amount', 'line_count', 'created_at']
    list_filter = ['invoice_date', 'created_at', 'is_deleted']
    search_fields = [
        'invoice_number', 'job__display_name', 'job__customer__business_name',
        'job__customer__contact_name', 'bill_to_name', 'notes_public', 'notes_private'
    ]
    ordering = ['-invoice_date', '-created_at']
    date_hierarchy = 'invoice_date'
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_number', 'invoice_date', 'job', 'work_order')
        }),
        ('Billing Information', {
            'fields': (
                'bill_to_name', 'bill_to_address_line1', 'bill_to_address_line2',
                'bill_to_city', 'bill_to_state', 'bill_to_postal_code', 'bill_to_phone'
            ),
            'description': 'Leave blank to use job customer information'
        }),
        ('Notes', {
            'fields': ('notes_public', 'notes_private')
        }),
        ('Totals', {
            'fields': ('subtotal', 'tax_rate', 'tax_amount', 'total_amount'),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('is_deleted', 'created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'subtotal', 'tax_amount', 'total_amount']
    
    def job_info(self, obj):
        """Display job information in the admin list"""
        return f"{obj.job.display_name} - {obj.job.trailer.display_name}"
    job_info.short_description = 'Job'
    
    def bill_to_display_name(self, obj):
        """Display billing name in the admin list"""
        return obj.bill_to_display_name
    bill_to_display_name.short_description = 'Bill To'
    
    def total_amount(self, obj):
        """Display total amount in the admin list"""
        return f"${obj.total_amount:.2f}"
    total_amount.short_description = 'Total'
    
    def line_count(self, obj):
        """Display line count in the admin list"""
        return obj.line_count
    line_count.short_description = 'Lines'
    
    def get_queryset(self, request):
        """Return invoices with related data"""
        return super().get_queryset(request).select_related('job__customer', 'job__trailer', 'work_order')


@admin.register(InvoiceLine)
class InvoiceLineAdmin(admin.ModelAdmin):
    """Admin configuration for InvoiceLine model"""
    list_display = ['invoice', 'item_code', 'description', 'qty', 'price', 'total', 'created_at']
    list_filter = ['created_at', 'invoice__invoice_date']
    search_fields = [
        'item_code', 'description', 'invoice__invoice_number',
        'invoice__job__display_name'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        ('Line Information', {
            'fields': ('invoice', 'item_code', 'description')
        }),
        ('Pricing', {
            'fields': ('qty', 'price', 'total')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'total']
    
    def get_queryset(self, request):
        """Return invoice lines with related data"""
        return super().get_queryset(request).select_related('invoice__job__customer', 'invoice__job__trailer')


@admin.register(StatusChange)
class StatusChangeAdmin(admin.ModelAdmin):
    """Admin configuration for StatusChange model"""
    list_display = ['job_info', 'old_status', 'new_status', 'changed_by', 'changed_at']
    list_filter = ['old_status', 'new_status', 'changed_at', 'changed_by']
    search_fields = [
        'job__display_name', 'job__customer__business_name', 'job__customer__contact_name',
        'changed_by__username', 'notes'
    ]
    ordering = ['-changed_at']
    date_hierarchy = 'changed_at'
    
    fieldsets = (
        ('Status Change Information', {
            'fields': ('job', 'old_status', 'new_status')
        }),
        ('Change Details', {
            'fields': ('changed_by', 'changed_at', 'notes')
        }),
    )
    
    readonly_fields = ['changed_at']
    
    def job_info(self, obj):
        """Display job information in the admin list"""
        return f"{obj.job.display_name} - {obj.job.trailer.display_name}"
    job_info.short_description = 'Job'
    
    def get_queryset(self, request):
        """Return status changes with related data"""
        return super().get_queryset(request).select_related('job__customer', 'job__trailer', 'changed_by')


@admin.register(PrintTemplateSetting)
class PrintTemplateSettingAdmin(admin.ModelAdmin):
    """Admin configuration for PrintTemplateSetting model"""
    list_display = ['template_name', 'template_type', 'company_name', 'is_active', 'created_at']
    list_filter = ['template_type', 'is_active', 'created_at', 'page_size', 'orientation']
    search_fields = [
        'template_name', 'company_name', 'company_phone', 'company_email'
    ]
    ordering = ['template_type', 'template_name']
    
    fieldsets = (
        ('Template Information', {
            'fields': ('template_name', 'template_type', 'is_active')
        }),
        ('Company Branding', {
            'fields': (
                'company_name', 'company_logo_path', 'company_address',
                'company_phone', 'company_email', 'company_website'
            )
        }),
        ('Document Styling', {
            'fields': (
                'header_color', 'text_color', 'accent_color',
                'font_family', 'font_size'
            )
        }),
        ('Layout Options', {
            'fields': (
                'show_logo', 'show_company_info', 'show_footer', 'footer_text'
            )
        }),
        ('Document Settings', {
            'fields': (
                'default_tax_rate', 'currency_symbol', 'page_size', 'orientation'
            )
        }),
        ('System', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        """Return print template settings with related data"""
        return super().get_queryset(request).select_related('created_by', 'updated_by')
