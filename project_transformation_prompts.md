# GTS Shop Scheduler - Project Transformation Prompts

This document contains a series of prompts to transform your current Django project into a comprehensive trailer repair & rental shop scheduling system. Each section can be worked on independently.

## Phase 1: Core Data Models

### 1.1 Calendar Model Setup
"Create a Calendar model for the trailer repair shop with fields: name (CharField, unique), color (CharField for CSS hex), and is_active (BooleanField). Include proper admin configuration and basic CRUD views."

### 1.2 Customer Model Enhancement
"Enhance the existing Customer model to include: business_name, contact_name, phone, alt_phone, email, address_line1, address_line2, city, state, postal_code, notes. Add database indexes for business_name, contact_name, and phone to optimize search performance."

### 1.3 Trailer Model Enhancement
"Enhance the existing Trailer model to include: customer (ForeignKey), serial_number, color, description. Add a search vector field spanning serial, color, and description for efficient global search."

### 1.4 Job Model Creation
"Create a comprehensive Job model with fields: calendar (FK to Calendar), status (choices: Scheduled, InProgress, Completed, Canceled), customer (FK), trailer (FK), business_name, contact_name, phone, address fields, date_call_received, start_dt, end_dt, all_day (Boolean), repeat_type (choices: None, Annual, EveryNMonths), repeat_n_months, repair_notes, trailer_color_overwrite, quote_text, is_deleted (soft delete), created_by, updated_by, and auto timestamps."

### 1.5 Work Order Models
"Create WorkOrder and WorkOrderLine models. WorkOrder: job (OneToOne), wo_number (unique), wo_date, notes. WorkOrderLine: work_order (FK), item_code, description, qty, rate, total (denormalized). Include proper related_name and constraints."

### 1.6 Invoice Models
"Create Invoice and InvoiceLine models. Invoice: job (FK), work_order (FK), invoice_number (unique), invoice_date, bill_to fields, notes_public/private, totals (subtotal/tax/total). InvoiceLine: invoice (FK), item_code, description, qty, price, total. Include proper validation and business logic."

### 1.7 Audit and Settings Models
"Create StatusChange model for job status audit trail and PrintTemplateSetting model for branding configuration. Include proper foreign keys and choice fields."

## Phase 2: Views and URL Structure

### 2.1 Calendar View Implementation
"Create a CalendarView that displays a color-coded monthly calendar with filters for calendar, status, and search. Include HTMX endpoints for grid updates, legend, and quick actions like drag/drop and status toggles."

### 2.2 Job List View
"Create a JobListView with sortable columns (Date, Name), filters (Status/Calendar), and free-text search across customer/phone/address/trailer info. Include HTMX pagination and real-time row updates."

### 2.3 Job CRUD Views
"Create JobCreateView, JobDetailView, and JobUpdateView with proper form handling, keyboard flow (Enter to advance), and HTMX field-level saves. Include validation and conflict detection."

### 2.4 Work Order Views
"Create WorkOrderDetailView with Repair List table management, HTMX line CRUD operations, and print views for internal and customer copy work orders."

### 2.5 Invoice Views
"Create InvoiceCreateFromWOView, InvoiceDetailView, and print views. Include line item management and proper business rules for quote field exclusion."

### 2.6 Global Search Implementation
"Create a SearchView with facet-based search across Customer Name, Trailer Info, Phone Number, and Address. Include HTMX endpoint for real-time results and pre-fill job forms."

### 2.7 Settings Views
"Create CalendarSettingsView and PrintTemplateSettingsView for managing calendars, colors, and print branding options."

## Phase 3: Templates and UI Components

### 3.1 Base Template Structure
"Update base.html with global navigation, toast messages, and HTMX/AlpineJS includes. Create reusable components for form fields, modals, tables, and status pills."

### 3.2 Calendar Templates
"Create calendar.html main view, grid.html partial for month display, day_cell.html for individual days, and job_chip.html for color-coded job display with completion styling."

### 3.3 Job Templates
"Create job form templates with proper field order for keyboard flow, detail view with tabs, and partials for header summary and status badges."

### 3.4 Work Order Templates
"Create work order detail templates with Repair List table, line management partials, and print templates for internal and customer copy views."

### 3.5 Invoice Templates
"Create invoice creation, detail, and print templates with proper line item management and customer-facing layouts."

### 3.6 Search and Settings Templates
"Create search interface with facet buttons and results display, plus settings pages for calendar and print template management."

## Phase 4: HTMX Interactions and JavaScript

### 4.1 Calendar Interactions
"Implement HTMX interactions for calendar filter chips, status filters, grid updates, and quick actions like drag/drop and completion toggles."

### 4.2 Job Form Interactions
"Implement keyboard flow (Enter to advance) in job forms, HTMX field-level saves, and real-time validation with conflict detection."

### 4.3 Work Order Line Management
"Create HTMX endpoints and JavaScript for adding, updating, and deleting work order lines with real-time total calculations."

### 4.4 Invoice Line Management
"Implement similar HTMX interactions for invoice line management with proper business rules and total calculations."

### 4.5 Global Search Interactions
"Create real-time search with HTMX, result selection for form pre-filling, and proper keyboard navigation."

## Phase 5: Business Logic and Validation

### 5.1 Job Validation Rules
"Implement validation for all-day events, repeat rules, date/time conflicts, and proper status transitions with audit trail."

### 5.2 Work Order Business Logic
"Create services for work order number generation, line total calculations, and proper relationships with jobs and invoices."

### 5.3 Invoice Business Logic
"Implement invoice number generation, line total calculations, tax handling, and proper quote field exclusion from print views."

### 5.4 Search and Performance
"Implement efficient search across multiple models with proper database indexes and search vector optimization."

### 5.5 Print Template Logic
"Create print template services for generating proper layouts for invoices, work orders, and customer copies with branding options."

## Phase 6: Styling and UX

### 6.1 Calendar Styling
"Implement color-coded calendar styling with proper completion states (line-through, opacity), responsive design, and accessibility features."

### 6.2 Form Styling
"Create modern form styling with proper focus states, keyboard navigation indicators, and responsive layouts for all CRUD operations."

### 6.3 Print Layouts
"Design print-friendly layouts for invoices, work orders, and customer copies with proper margins, typography, and branding options."

### 6.4 Status and Filter Styling
"Create consistent styling for status badges, filter chips, and interactive elements with proper hover and focus states."

## Phase 7: Advanced Features

### 7.1 Repeat Job Generation
"Implement background services for generating repeat jobs (annual or every N months) with proper scheduling and conflict detection."

### 7.2 Export and Integration
"Create export functionality for invoices and work orders, plus API endpoints for potential external accounting system integration."

### 7.3 Permissions and Security
"Implement proper Django permissions for different user roles (Viewer, Editor, Billing, Admin) with appropriate view and action restrictions."

### 7.4 Performance Optimization
"Optimize database queries, implement caching for calendar views, and add proper indexing for search performance."

## Phase 8: Testing and Documentation

### 8.1 Model Testing
"Create comprehensive tests for all models, including validation rules, business logic, and relationship integrity."

### 8.2 View Testing
"Test all views and HTMX endpoints with proper authentication, permissions, and edge cases."

### 8.3 Integration Testing
"Create end-to-end tests for complete workflows like job creation → work order → invoice generation."

### 8.4 Documentation
"Create user documentation for the scheduling system, including keyboard shortcuts, workflow descriptions, and troubleshooting guides."

## Usage Instructions

1. Work through each phase in order
2. Each prompt can be executed independently
3. Test thoroughly after each major change
4. Keep the existing Django/HTMX architecture intact
5. Maintain consistency with your current color palette and styling preferences

## Notes

- Preserve existing functionality where possible
- Use Django best practices and HTMX for dynamic interactions
- Maintain the current project structure and naming conventions
- Focus on keyboard accessibility and fast data entry
- Ensure print layouts are professional and customer-ready

