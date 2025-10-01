from django.urls import path
from .views import (
    HomeView,
    CalendarView,
    get_job_calendar_data,
    update_job_status,
    delete_job_api,
    CalendarListView,
    CalendarCreateView,
    CalendarUpdateView,
    CalendarDeleteView,
    JobListView,
    job_create,
    JobDetailView,
    JobUpdateView,
    JobDeleteView,
    JobPrintWOView,
    JobPrintWOCustomerView,
    JobPrintInvoiceView,
    WorkOrderListView,
    WorkOrderDetailView,
    WorkOrderCreateView,
    WorkOrderUpdateView,
    WorkOrderDeleteView,
    WorkOrderPrintView,
    WorkOrderCustomerPrintView,
    InvoiceListView,
    InvoiceDetailView,
    job_detail_modal,
    job_edit_modal,
    job_detail_panel,
    job_edit_panel,
    job_create_panel,
    job_create_partial,
    job_detail_partial,
    job_create_submit,
    job_create_api,
    job_update_api,
    job_detail_api,
    workorder_add_line_api,
)
from . import error_views

app_name = 'rental_scheduler'

urlpatterns = [
    # Home and Calendar
    path('', CalendarView.as_view(), name='home'),
    path('calendar/', CalendarView.as_view(), name='calendar'),
    
    # Calendar API
    path('api/job-calendar-data/', get_job_calendar_data, name='job_calendar_data'),
    path('api/jobs/create/', job_create_api, name='job_create_api'),
    path('api/jobs/<int:job_id>/update-status/', update_job_status, name='update_job_status'),
    path('api/jobs/<int:job_id>/delete/', delete_job_api, name='delete_job_api'),
    path('api/jobs/<int:pk>/update/', job_update_api, name='job_update_api'),
    path('api/jobs/<int:pk>/detail/', job_detail_api, name='job_detail_api'),
    
    # Calendar Management URLs
    path('calendars/', CalendarListView.as_view(), name='calendar_list'),
    path('calendars/create/', CalendarCreateView.as_view(), name='calendar_create'),
    path('calendars/<int:pk>/edit/', CalendarUpdateView.as_view(), name='calendar_update'),
    path('calendars/<int:pk>/delete/', CalendarDeleteView.as_view(), name='calendar_delete'),
    
    # Job URLs
    path('jobs/', JobListView.as_view(), name='job_list'),
    path('jobs/create/', job_create, name='job_create'),
    path('jobs/<int:pk>/', JobDetailView.as_view(), name='job_detail'),
    path('jobs/<int:pk>/edit/', JobUpdateView.as_view(), name='job_update'),
    path('jobs/<int:pk>/delete/', JobDeleteView.as_view(), name='job_delete'),
    path('jobs/<int:pk>/print/wo/', JobPrintWOView.as_view(), name='job_print_wo'),
    path('jobs/<int:pk>/print/wo-customer/', JobPrintWOCustomerView.as_view(), name='job_print_wo_customer'),
    path('jobs/<int:pk>/print/invoice/', JobPrintInvoiceView.as_view(), name='job_print_invoice'),
    
    # Job Modal URLs
    path('jobs/<int:pk>/detail/', job_detail_modal, name='job_detail_modal'),
    path('jobs/<int:pk>/edit-modal/', job_edit_modal, name='job_edit_modal'),
    
    # Job Panel URLs
    path('jobs/<int:pk>/detail-panel/', job_detail_panel, name='job_detail_panel'),
    path('jobs/<int:pk>/edit-panel/', job_edit_panel, name='job_edit_panel'),
    path('jobs/create-panel/', job_create_panel, name='job_create_panel'),
    
    # Job Partial URLs
    path('jobs/new/partial/', job_create_partial, name='job_create_partial'),
    path('jobs/<int:pk>/partial/', job_detail_partial, name='job_detail_partial'),
    path('jobs/new/submit/', job_create_submit, name='job_create_submit'),
    
    # Work Order URLs
    path('workorders/', WorkOrderListView.as_view(), name='workorder_list'),
    path('workorders/create/', WorkOrderCreateView.as_view(), name='workorder_create'),
    path('workorders/<int:pk>/', WorkOrderDetailView.as_view(), name='workorder_detail'),
    path('workorders/<int:pk>/edit/', WorkOrderUpdateView.as_view(), name='workorder_update'),
    path('workorders/<int:pk>/delete/', WorkOrderDeleteView.as_view(), name='workorder_delete'),
    path('workorders/<int:pk>/print/', WorkOrderPrintView.as_view(), name='workorder_print'),
    path('workorders/<int:pk>/print/customer/', WorkOrderCustomerPrintView.as_view(), name='workorder_customer_print'),
    
    # Invoice Management URLs
    path('invoices/', InvoiceListView.as_view(), name='invoice_list'),
    path('invoices/<int:pk>/', InvoiceDetailView.as_view(), name='invoice_detail'),
    
    # API endpoints
    path('api/workorders/<int:pk>/add-line/', workorder_add_line_api, name='workorder_add_line_api'),
    path('api/send-error-report/', error_views.send_error_report, name='send_error_report'),
]
