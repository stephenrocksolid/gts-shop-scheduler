# JSON Export/Import Feature Guide

## Overview

The JSON export/import feature allows you to transfer job/event data between different instances of the GTS Scheduler application. This is useful for:
- Migrating data to a new server
- Creating backups of calendar data
- Sharing job data between different installations
- Testing data in a development environment

## Features

- **Complete Data Preservation**: All job fields are exported including:
  - Contact information (business name, contact name, phone, address)
  - Scheduling details (dates, times, all-day flag)
  - Job status (completed, uncompleted, pending, canceled)
  - Trailer information (color, serial, details)
  - Repair notes and quotes
  - Call reminders and completion status
  - Recurring event rules and relationships
  
- **Calendar Remapping**: When importing, you can choose which calendar to assign all imported jobs to, regardless of their original calendar

- **Batch Tracking**: Each import is assigned a unique batch ID, allowing you to:
  - View import history
  - Revert entire imports if needed
  - Track which jobs came from which import

- **Transaction Safety**: Imports use database transactions, ensuring all-or-nothing imports (if any job fails, the entire import is rolled back)

## How to Export Jobs

### Export All Jobs

1. Navigate to **Job List** page
2. Click the **"Export Jobs"** button (purple button in the top right)
3. A JSON file will be downloaded with all jobs from all calendars
4. The filename will be: `jobs_export_all_YYYY-MM-DD_HHMMSS.json`

### Export Jobs from a Specific Calendar

1. Navigate to **Calendars** page
2. Find the calendar you want to export
3. Click the **"Export"** button in the Actions column for that calendar
4. A JSON file will be downloaded with only jobs from that calendar
5. The filename will be: `jobs_export_[CalendarName]_YYYY-MM-DD_HHMMSS.json`

## How to Import Jobs

1. Navigate to **Job List** page
2. Click the **"Import Jobs"** button (green button in the top right)
3. Select the destination calendar from the dropdown
   - All imported jobs will be assigned to this calendar
   - This allows you to import jobs from one calendar into a different calendar
4. Click **"Choose File"** and select the JSON export file
5. Click **"Import Jobs"**
6. You'll see a success message with the number of jobs imported and the batch ID

## JSON File Structure

The export file follows this structure:

```json
{
  "version": "1.0",
  "exported_at": "2025-10-27T10:30:00Z",
  "export_source": "Shop" or "all",
  "job_count": 42,
  "jobs": [
    {
      "business_name": "ABC Company",
      "contact_name": "John Doe",
      "phone": "(555) 123-4567",
      "address_line1": "123 Main St",
      "city": "Springfield",
      "state": "IL",
      "postal_code": "62701",
      "start_dt": "2025-11-01T09:00:00+00:00",
      "end_dt": "2025-11-01T17:00:00+00:00",
      "all_day": false,
      "status": "uncompleted",
      "trailer_color": "White",
      "trailer_serial": "ABC123",
      "notes": "Regular maintenance",
      "repair_notes": "Check brakes and lights",
      "quote": "250.00",
      "has_call_reminder": true,
      "call_reminder_weeks_prior": 1,
      "call_reminder_completed": false,
      "recurrence_rule": null,
      ...
    }
  ]
}
```

## Important Notes

### Recurring Events
- Recurring event parent-child relationships are preserved during export/import
- Both parent jobs and their instances are exported
- The relationships are automatically reconstructed during import

### Timestamps
- All timestamps are exported in ISO 8601 format with timezone information
- The import process handles timezone conversions automatically

### Validation
- The import validates the JSON structure before processing
- Invalid files will be rejected with clear error messages
- Maximum file size: 50 MB

### Import Batch Tracking
- Each import is assigned a unique UUID batch ID
- This allows you to view all imports in the **Import History** page
- You can revert an entire import batch if needed

### Compatibility
- Export files are compatible only with the same version of this software
- The `version` field in the export ensures compatibility
- Future versions may support multiple export versions

## Troubleshooting

### Import Fails with "Invalid JSON structure"
- Ensure the file is a valid JSON export from this application
- Check that the file hasn't been manually edited
- Verify the file isn't corrupted

### Some Jobs Don't Import
- Check that required fields (business_name, start_dt, end_dt) are present
- Verify date formats are valid ISO 8601
- Check the error message for specific field issues

### Export Downloads Empty File
- Ensure there are jobs in the selected calendar or database
- Check browser console for JavaScript errors
- Try a different browser

### "No calendars found" Error During Import
- Create at least one active calendar before importing
- Inactive calendars won't appear in the destination calendar dropdown

## Related Features

- **ICS Import**: For importing from external calendar applications (Thunderbird, etc.)
- **Import History**: View and manage all previous imports
- **Revert Import**: Undo an entire import batch

## Technical Details

### File Format
- Format: JSON (JavaScript Object Notation)
- Encoding: UTF-8
- Pretty-printed with 2-space indentation for readability

### Security
- Imports use CSRF protection
- File size limits prevent abuse
- Batch tracking enables audit trails

### Performance
- Large imports (1000+ jobs) may take several seconds
- Imports are processed in a single database transaction
- Memory efficient processing (streaming)






