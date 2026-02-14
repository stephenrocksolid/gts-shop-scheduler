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
    JobListTablePartialView,
    JobDeleteView,
    JobPrintInvoiceView,
    workorder_employee_settings,
    workorder_new,
    workorder_edit,
    workorder_pdf,
    workorder_pdf_preview,
    InvoiceListView,
    InvoiceDetailView,
    job_create_partial,
    job_detail_partial,
    job_create_submit,
    job_create_api,
    job_update_api,
    job_detail_api,
    accounting_customers_search,
    accounting_customers_create,
    accounting_customers_update,
    accounting_items_search,
    work_order_customer_tax_rate,
    work_order_compute_totals,
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
    recurrence_preview_occurrences,
    series_occurrences_api,
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
    path('api/recurrence/preview/', recurrence_preview_occurrences, name='recurrence_preview_occurrences'),
    path('api/recurrence/series-occurrences/', series_occurrences_api, name='series_occurrences_api'),
    
    # Calendar Management URLs
    path('calendars/', CalendarListView.as_view(), name='calendar_list'),
    path('calendars/create/', CalendarCreateView.as_view(), name='calendar_create'),
    path('calendars/<int:pk>/edit/', CalendarUpdateView.as_view(), name='calendar_update'),
    path('calendars/<int:pk>/delete/', CalendarDeleteView.as_view(), name='calendar_delete'),
    
    # Job URLs
    path('jobs/', JobListView.as_view(), name='job_list'),
    path('jobs/partial/table/', JobListTablePartialView.as_view(), name='job_list_table_partial'),
    path('jobs/import/', calendar_import, name='calendar_import'),
    path('jobs/import/history/', import_history, name='import_history'),
    path('jobs/import/<str:batch_id>/revert/', revert_import, name='revert_import'),
    path('jobs/import/json/', import_jobs_json, name='job_import_json'),
    path('jobs/export/', export_jobs, name='job_export'),
    path('jobs/export/<int:calendar_id>/', export_jobs, name='job_export_calendar'),
    path('jobs/<int:pk>/delete/', JobDeleteView.as_view(), name='job_delete'),
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
    
    # Work Order URLs (v2)
    path('settings/workorders/employees/', workorder_employee_settings, name='workorder_employee_settings'),
    path('workorders/new/', workorder_new, name='workorder_new'),
    path('workorders/<int:pk>/edit/', workorder_edit, name='workorder_edit'),
    # PDF print (v2)
    path('workorders/<int:pk>/pdf/', workorder_pdf, name='workorder_pdf'),
    path('workorders/<int:pk>/pdf/preview/', workorder_pdf_preview, name='workorder_pdf_preview'),
    
    # Invoice Management URLs
    path('invoices/', InvoiceListView.as_view(), name='invoice_list'),
    path('invoices/<int:pk>/', InvoiceDetailView.as_view(), name='invoice_detail'),
    
    # API endpoints
    # Accounting-backed APIs (Classic Accounting)
    path('api/accounting/customers/search/', accounting_customers_search, name='accounting_customers_search'),
    path('api/accounting/customers/create/', accounting_customers_create, name='accounting_customers_create'),
    path('api/accounting/customers/<int:orgid>/update/', accounting_customers_update, name='accounting_customers_update'),
    path('api/accounting/items/search/', accounting_items_search, name='accounting_items_search'),
    path('api/work-orders/customer-tax-rate/', work_order_customer_tax_rate, name='work_order_customer_tax_rate'),
    path('api/work-orders/compute-totals/', work_order_compute_totals, name='work_order_compute_totals'),
    path('api/send-error-report/', error_views.send_error_report, name='send_error_report'),
]
