# Template Organization

This document describes the organization and structure of the Django templates in the GTS Rental Scheduler application.

## Directory Structure

```
rental_scheduler/templates/
├── base.html                          # Main base template
├── error/                             # Error page templates
│   ├── 400.html
│   ├── 403.html
│   ├── 404.html
│   ├── 500.html
│   └── error_base.html
└── rental_scheduler/                  # App-specific templates
    ├── layouts/                       # Base layout templates
    │   ├── app_base.html             # Main app layout
    │   ├── form_base.html            # Form layout template
    │   └── list_base.html            # List layout template
    ├── components/                    # Reusable components
    │   ├── action_buttons.html       # Action button groups
    │   ├── button.html               # Button component
    │   ├── empty_state.html          # Empty state component
    │   ├── loading.html              # Loading component
    │   ├── page_header.html          # Page header component
    │   └── status_pill.html          # Status indicator
    ├── includes/                      # Global UI shells included by base.html
    │   ├── panel.html                # Floating Job Panel shell
    │   └── workspace_bar.html        # Bottom Job Workspace tab bar
    ├── partials/                      # Template partials
    │   ├── job_list_table.html
    │   ├── job_row.html
    │   └── work_order_line.html
    ├── jobs/                          # Job-related templates
    │   ├── job_list.html
    │   ├── _job_form_partial.html
    │   ├── _job_detail_partial.html
    │   ├── job_confirm_delete.html
    │   ├── job_import.html
    │   ├── job_import_json.html
    │   └── import_history.html
    ├── call_reminders/                # Call reminder partials
    │   └── _call_reminder_form_partial.html
    ├── workorders_v2/                 # Work order v2 templates
    │   ├── workorder_form.html
    │   └── workorder_pdf.html
    ├── calendars/                     # Calendar templates
    │   ├── calendar_confirm_delete.html
    │   ├── calendar_form.html
    │   ├── calendar_list.html
    ├── calendar.html                  # Main calendar page
    └── home.html                      # Home page template
```

## Template Hierarchy

### Base Templates
- **`base.html`**: Main base template with navigation, footer, and common scripts
- **`rental_scheduler/layouts/app_base.html`**: App-specific base with common styling
- **`rental_scheduler/layouts/form_base.html`**: Form-specific layout with error handling
- **`rental_scheduler/layouts/list_base.html`**: List-specific layout with pagination

### Component Templates
- **`components/`**: Reusable UI components that can be included in any template
- **`partials/`**: Template fragments for specific functionality
- **`includes/`**: Global shells included by `base.html` (Job Panel + Workspace bar)

### Feature-Specific Templates
- **`jobs/`**: All job-related templates (CRUD operations, modals, prints)
- **`workorders_v2/`**: Work order v2 templates (revamp)
- **`calendars/`**: All calendar-related templates

## Naming Conventions

### File Naming
- Use lowercase with underscores: `job_list.html`
- Use descriptive names: `job_list.html` not `list.html`
- Prefix partial templates with underscore: `_job_form_partial.html`

### Template Blocks
- Use descriptive block names: `{% block page_title %}`
- Follow consistent naming: `page_*`, `form_*`, `list_*`
- Use semantic names: `main_content` not `content`

## Best Practices

### Template Inheritance
1. Always extend the appropriate base template
2. Use the layout templates for consistent structure
3. Override only the blocks you need to customize

### Component Usage
1. Use components for reusable UI elements
2. Pass data to components via template context
3. Keep components focused and single-purpose

### Code Organization
1. Group related templates in feature directories
2. Use partials for complex template fragments
3. Keep templates focused and readable

### Styling
1. Use Tailwind CSS classes consistently
2. Follow the design system defined in components
3. Use semantic HTML structure

## Migration Guide

### From Old Templates to New Layout System

1. **Replace base template extension**:
   ```django
   <!-- Old -->
   {% extends "base.html" %}
   
   <!-- New -->
   {% extends "rental_scheduler/layouts/app_base.html" %}
   ```

2. **Use layout-specific templates**:
   ```django
   <!-- For forms -->
   {% extends "rental_scheduler/layouts/form_base.html" %}
   
   <!-- For lists -->
   {% extends "rental_scheduler/layouts/list_base.html" %}
   ```

3. **Use components for common elements**:
   ```django
   <!-- Page header -->
   {% include "rental_scheduler/components/page_header.html" with page_title="My Page" %}
   
   <!-- Action buttons -->
   {% include "rental_scheduler/components/action_buttons.html" with edit_url="..." %}
   ```

4. **Use semantic blocks**:
   ```django
   {% block page_title %}My Page Title{% endblock %}
   {% block form_fields %}...{% endblock %}
   {% block list_content %}...{% endblock %}
   ```

## Future Improvements

1. **Template Caching**: Implement template fragment caching for better performance
2. **Component Library**: Expand the component library with more reusable elements
3. **Theme System**: Implement a theme system for different user preferences
4. **Accessibility**: Ensure all templates meet WCAG accessibility standards
5. **Mobile Optimization**: Optimize templates for mobile devices
