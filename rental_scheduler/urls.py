from django.urls import path
from .views import (
    HomeView,
    CalendarView,
    get_job_calendar_data,
    update_job_status,
    delete_job_api,
    mark_call_reminder_complete,
    call_reminder_create_partial,
    call_reminder_create_submit,
    call_reminder_update,
    call_reminder_delete,
    job_call_reminder_update,
    CalendarListView,
    CalendarCreateView,
    CalendarUpdateView,
    CalendarDeleteView,
    JobListView,
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
    job_create_partial,
    job_detail_partial,
    job_create_submit,
    job_create_api,
    job_update_api,
    job_detail_api,
    workorder_add_line_api,
    calendar_import,
    import_history,
    revert_import,
    export_jobs,
    import_jobs_json,
)
from .views_recurring import (
    job_create_api_recurring,
    job_update_api_recurring,
    job_cancel_future_api,
    job_delete_api_recurring,
    materialize_occurrence_api,
)
from . import error_views

app_name = 'rental_scheduler'

urlpatterns = [
    # Home and Calendar
    path('', CalendarView.as_view(), name='home'),
    path('calendar/', CalendarView.as_view(), name='calendar'),
    
    # Calendar API
    path('api/job-calendar-data/', get_job_calendar_data, name='job_calendar_data'),
    path('api/jobs/create/', job_create_api_recurring, name='job_create_api'),  # Updated to use recurring version
    path('api/jobs/<int:job_id>/update-status/', update_job_status, name='update_job_status'),
    path('api/jobs/<int:job_id>/delete/', delete_job_api, name='delete_job_api'),
    path('api/jobs/<int:job_id>/mark-call-reminder-complete/', mark_call_reminder_complete, name='mark_call_reminder_complete'),
    path('api/jobs/<int:pk>/update/', job_update_api_recurring, name='job_update_api'),  # Updated to use recurring version
    path('api/jobs/<int:pk>/detail/', job_detail_api, name='job_detail_api'),
    
    # Recurring Events API
    path('api/jobs/<int:pk>/cancel-future/', job_cancel_future_api, name='job_cancel_future_api'),
    path('api/jobs/<int:pk>/delete-recurring/', job_delete_api_recurring, name='job_delete_api_recurring'),
    path('api/recurrence/materialize/', materialize_occurrence_api, name='materialize_occurrence_api'),
    
    # Calendar Management URLs
    path('calendars/', CalendarListView.as_view(), name='calendar_list'),
    path('calendars/create/', CalendarCreateView.as_view(), name='calendar_create'),
    path('calendars/<int:pk>/edit/', CalendarUpdateView.as_view(), name='calendar_update'),
    path('calendars/<int:pk>/delete/', CalendarDeleteView.as_view(), name='calendar_delete'),
    
    # Job URLs
    path('jobs/', JobListView.as_view(), name='job_list'),
    path('jobs/import/', calendar_import, name='calendar_import'),
    path('jobs/import/history/', import_history, name='import_history'),
    path('jobs/import/<str:batch_id>/revert/', revert_import, name='revert_import'),
    path('jobs/import/json/', import_jobs_json, name='job_import_json'),
    path('jobs/export/', export_jobs, name='job_export'),
    path('jobs/export/<int:calendar_id>/', export_jobs, name='job_export_calendar'),
    path('jobs/<int:pk>/delete/', JobDeleteView.as_view(), name='job_delete'),
    path('jobs/<int:pk>/print/wo/', JobPrintWOView.as_view(), name='job_print_wo'),
    path('jobs/<int:pk>/print/wo-customer/', JobPrintWOCustomerView.as_view(), name='job_print_wo_customer'),
    path('jobs/<int:pk>/print/invoice/', JobPrintInvoiceView.as_view(), name='job_print_invoice'),
    
    # Job Modal URLs
    
    # Job Partial URLs
    path('jobs/new/partial/', job_create_partial, name='job_create_partial'),
    path('jobs/<int:pk>/partial/', job_detail_partial, name='job_detail_partial'),
    path('jobs/new/submit/', job_create_submit, name='job_create_submit'),
    
    # Call Reminder URLs
    path('call-reminders/new/partial/', call_reminder_create_partial, name='call_reminder_create_partial'),
    path('call-reminders/create/', call_reminder_create_submit, name='call_reminder_create_submit'),
    path('call-reminders/<int:pk>/update/', call_reminder_update, name='call_reminder_update'),
    path('call-reminders/<int:pk>/delete/', call_reminder_delete, name='call_reminder_delete'),
    path('jobs/<int:job_id>/call-reminder/update/', job_call_reminder_update, name='job_call_reminder_update'),
    
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
