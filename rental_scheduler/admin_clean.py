from django.contrib import admin
from .models import Calendar, Job, WorkOrder, WorkOrderLine, Invoice, InvoiceLine, StatusChange

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


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    """Admin configuration for Job model"""
    list_display = ['display_name', 'trailer_info', 'calendar', 'status', 'start_dt', 'end_dt', 'is_overdue_display']
    list_filter = ['status', 'calendar', 'all_day', 'repeat_type', 'is_deleted', 'start_dt', 'created_at']
    search_fields = [
        'business_name', 'contact_name', 'phone', 'address_line1', 'city',
        'trailer_color', 'trailer_serial', 'trailer_details',
        'repair_notes', 'quote_text'
    ]
    ordering = ['-start_dt']
    date_hierarchy = 'start_dt'
    
    fieldsets = (
        ('Scheduling', {
            'fields': ('calendar', 'status', 'start_dt', 'end_dt', 'all_day')
        }),
        ('Contact Information', {
            'fields': ('business_name', 'contact_name', 'phone'),
        }),
        ('Address Information', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'postal_code'),
        }),
        ('Trailer Information', {
            'fields': ('trailer_color', 'trailer_serial', 'trailer_details'),
        }),
        ('Job Details', {
            'fields': ('date_call_received', 'notes', 'repair_notes', 'quote', 'quote_text')
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
        return f"{obj.trailer_color or 'Unknown'} Trailer"
    trailer_info.short_description = 'Trailer'
    
    def is_overdue_display(self, obj):
        """Display overdue status in the admin list"""
        if obj.is_overdue:
            return "⚠️ OVERDUE"
        return ""
    is_overdue_display.short_description = 'Status'
    
    def get_queryset(self, request):
        """Return jobs ordered by start date (newest first)"""
        return super().get_queryset(request).select_related('calendar')


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    """Admin configuration for WorkOrder model"""
    list_display = ['wo_number', 'job_info', 'wo_date', 'total_amount', 'line_count', 'created_at']
    list_filter = ['wo_date', 'created_at']
    search_fields = [
        'wo_number', 'job__business_name', 'job__contact_name', 'notes'
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
        return f"{obj.job.display_name}"
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
        return super().get_queryset(request).select_related('job__calendar')


@admin.register(WorkOrderLine)
class WorkOrderLineAdmin(admin.ModelAdmin):
    """Admin configuration for WorkOrderLine model"""
    list_display = ['work_order', 'item_code', 'description', 'qty', 'rate', 'total', 'created_at']
    list_filter = ['created_at', 'work_order__wo_date']
    search_fields = [
        'item_code', 'description', 'work_order__wo_number',
        'work_order__job__business_name', 'work_order__job__contact_name'
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
        return super().get_queryset(request).select_related('work_order__job__calendar')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Admin configuration for Invoice model"""
    list_display = ['invoice_number', 'job_info', 'invoice_date', 'bill_to_display_name', 'total_amount', 'line_count', 'created_at']
    list_filter = ['invoice_date', 'created_at', 'is_deleted']
    search_fields = [
        'invoice_number', 'job__business_name', 'job__contact_name',
        'bill_to_name', 'notes_public', 'notes_private'
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
        return f"{obj.job.display_name}"
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
        return super().get_queryset(request).select_related('job__calendar', 'work_order')


@admin.register(InvoiceLine)
class InvoiceLineAdmin(admin.ModelAdmin):
    """Admin configuration for InvoiceLine model"""
    list_display = ['invoice', 'item_code', 'description', 'qty', 'price', 'total', 'created_at']
    list_filter = ['created_at', 'invoice__invoice_date']
    search_fields = [
        'item_code', 'description', 'invoice__invoice_number',
        'invoice__job__business_name', 'invoice__job__contact_name'
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
        return super().get_queryset(request).select_related('invoice__job__calendar')


@admin.register(StatusChange)
class StatusChangeAdmin(admin.ModelAdmin):
    """Admin configuration for StatusChange model"""
    list_display = ['job_info', 'old_status', 'new_status', 'changed_by', 'changed_at']
    list_filter = ['old_status', 'new_status', 'changed_at', 'changed_by']
    search_fields = [
        'job__business_name', 'job__contact_name',
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
        return f"{obj.job.display_name}"
    job_info.short_description = 'Job'
    
    def get_queryset(self, request):
        """Return status changes with related data"""
        return super().get_queryset(request).select_related('job__calendar', 'changed_by')
