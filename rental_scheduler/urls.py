from django.urls import path
from .views import (
    SystemSettingsUpdateView, 
    HomeView,
    TrailerCategoryListView,
    TrailerCategoryCreateView,
    TrailerCategoryUpdateView,
    TrailerCategoryDeleteView,
    TrailerListView,
    TrailerCreateView,
    TrailerUpdateView,
    TrailerDeleteView,
    TrailerServiceCreateView,
    TrailerServiceManagementView,
    TrailerServiceUpdateView,
    TrailerServiceDeleteView,
    end_service_early,
    browse_folders,
    ContractListView,
    ContractDetailView,
    ContractCreateView,
    ContractUpdateView,
    ContractDeleteView,
    update_contract_status,
    contract_status_toggle,
    get_available_trailers,
    search_customers,
    CalendarView,
    get_calendar_data,
    ContractPDFView,
    AvailabilityView,
    availability_search,
    test_404,
    test_500,
    test_403,
    test_400,
    validate_network_path,
    get_network_status,
    test_network_connection,
)
from .services.api_views import (
    calculate_rental_quote,
    get_calculation_constants,
    calculate_duration_info,
)
from . import error_views

app_name = 'rental_scheduler'

urlpatterns = [
    path('', CalendarView.as_view(), name='home'),
    path('settings/', SystemSettingsUpdateView.as_view(), name='settings_update'),
    path('availability/', AvailabilityView.as_view(), name='availability'),
    # Test error pages
    path('test/404/', test_404, name='test_404'),
    path('test/500/', test_500, name='test_500'),
    path('test/403/', test_403, name='test_403'),
    path('test/400/', test_400, name='test_400'),
    # Trailer Category URLs
    path('categories/', TrailerCategoryListView.as_view(), name='category_list'),
    path('categories/create/', TrailerCategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', TrailerCategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', TrailerCategoryDeleteView.as_view(), name='category_delete'),
    # Trailer URLs
    path('trailers/', TrailerListView.as_view(), name='trailer_list'),
    path('trailers/filter/', TrailerListView.as_view(), name='trailer_filter'),
    path('trailers/create/', TrailerCreateView.as_view(), name='trailer_create'),
    path('trailers/<int:pk>/edit/', TrailerUpdateView.as_view(), name='trailer_update'),
    path('trailers/<int:pk>/delete/', TrailerDeleteView.as_view(), name='trailer_delete'),
    # Trailer Service URLs
    path('trailers/<int:trailer_pk>/service/', TrailerServiceManagementView.as_view(), name='trailer_service_create'),
    path('trailers/<int:trailer_pk>/service/management/', TrailerServiceManagementView.as_view(), name='trailer_service_management'),
    path('trailers/<int:trailer_pk>/service/new/', TrailerServiceCreateView.as_view(), name='trailer_service_add'),
    path('service/<int:pk>/update/', TrailerServiceUpdateView.as_view(), name='trailer_service_update'),
    path('service/<int:pk>/delete/', TrailerServiceDeleteView.as_view(), name='trailer_service_delete'),
    path('service/<int:pk>/end-early/', end_service_early, name='end_service_early'),
    path('api/browse-folders/', browse_folders, name='browse_folders'),
    path('api/validate-network-path/', validate_network_path, name='validate_network_path'),
    path('api/test-network-connection/', test_network_connection, name='test_network_connection'),
    path('api/network-status/', get_network_status, name='get_network_status'),
    # Contract URLs
    path('contracts/', ContractListView.as_view(), name='contract_list'),
    path('contracts/<int:pk>/', ContractDetailView.as_view(), name='contract_detail'),
    path('contracts/create/', ContractCreateView.as_view(), name='contract_create'),
    path('contracts/<int:pk>/update/', ContractUpdateView.as_view(), name='contract_update'),
    path('contracts/<int:pk>/delete/', ContractDeleteView.as_view(), name='contract_delete'),
    path('contracts/<int:pk>/pdf/', ContractPDFView.as_view(), name='contract_pdf'),
    # Contract status endpoints
    path('contracts/<int:pk>/status/', contract_status_toggle, name='contract_status_toggle'),
    path('api/contracts/<int:pk>/update-status/', update_contract_status, name='update_contract_status'),
    path('api/contracts/get-available-trailers/', get_available_trailers, name='get_available_trailers'),
    # API endpoints
    path('api/search_customers/', search_customers, name='search_customers'),
    path('api/send-error-report/', error_views.send_error_report, name='send_error_report'),
    # Calculation API endpoints
    path('api/calculate-rental-quote/', calculate_rental_quote, name='calculate_rental_quote'),
    path('api/calculation-constants/', get_calculation_constants, name='get_calculation_constants'),
    path('api/calculate-duration/', calculate_duration_info, name='calculate_duration_info'),
    # Availability API endpoints
    path('api/availability/search/', availability_search, name='availability_search'),
    # Calendar URLs
    path('calendar/', CalendarView.as_view(), name='calendar'),
    path('api/calendar-data/', get_calendar_data, name='calendar_data'),
]