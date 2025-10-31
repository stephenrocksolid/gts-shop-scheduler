# Quick Start Guide: Importing Thunderbird Calendars

## Step-by-Step Instructions

### 1. Start Your Server
```bash
python manage.py runserver
```

### 2. Access the Import Page
Three ways to get there:
- Visit: `http://localhost:8000/jobs/import/`
- Navigate to **Jobs** page and click **"Import Calendar"** button
- From the main navigation menu

### 3. Prepare Your Calendar Export

#### In Mozilla Thunderbird:
1. Open Thunderbird Calendar
2. Right-click on the calendar you want to export
3. Select **"Export Calendar..."**
4. Choose **iCalendar (.ics)** format
5. Save the file to your computer

#### Your file is ready when:
- ✅ It has a `.ics` extension
- ✅ It's under 10MB in size
- ✅ It contains the events you want to import

### 4. Import Your Calendar

1. **Select Target Calendar**
   - Choose which calendar in your system should receive these events
   - Only active calendars will appear in the dropdown

2. **Upload Your File**
   - Click "Choose File" or drag-and-drop
   - Select your `.ics` file
   - File must be under 10MB

3. **Review Field Mapping** (displayed on page)
   - Event Title → Business Name
   - Description → Notes
   - Created Date → Date Call Received
   - Start/End Dates → Job dates
   - Recurring Rules → Preserved
   - Status → All set to "Uncompleted"

4. **Click "Import Events"**

### 5. Review Results

The results page shows:
- **Green Box**: Number of successfully imported events
- **Yellow Box**: Number of skipped events (missing required data)
- **Red Box**: Number of events with errors

If there are errors, you'll see details about:
- Which events failed
- Why they failed
- What you can do to fix them

### 6. Navigate to Your Events

From the results page:
- **View Calendar** - See events in calendar view
- **View Job List** - See events in list view
- **Import Another File** - Import more events

## What Gets Imported

### ✅ Imported Fields:
- **Business Name**: Event title (with phone extracted)
- **Phone**: Extracted from title if present
- **Notes**: Full event description
- **Start Date/Time**: Event start
- **End Date/Time**: Event end
- **All-Day Flag**: Auto-detected from event type
- **Date Call Received**: Event creation date
- **Recurring Rules**: Preserved for recurring events
- **Status**: Set to "Uncompleted"

### ❌ Not Imported:
- Event location (no matching field)
- Event categories (no matching field)
- Event attendees (no matching field)
- Event status (all become "Uncompleted")

## Examples of What It Does

### Example 1: Simple Event
**Thunderbird Event:**
```
Title: COLE ALEXANDER 740-501-9004
Description: PJ Dump repair needed
Start: Nov 15, 2021 (all-day)
End: Nov 26, 2021 (all-day)
```

**Becomes Job:**
```
Business Name: COLE ALEXANDER
Phone: 740-501-9004
Notes: PJ Dump repair needed
Start: Nov 15, 2021 00:00
End: Nov 26, 2021 23:59
All-Day: Yes
Status: Uncompleted
```

### Example 2: Recurring Event
**Thunderbird Event:**
```
Title: Annual Inspection
RRULE: FREQ=YEARLY;COUNT=5
Start: Jan 15, 2024
```

**Becomes Job:**
```
Business Name: Annual Inspection
Recurrence Rule: {"type": "yearly", "interval": 1, "count": 5}
Start: Jan 15, 2024
Status: Uncompleted
(Will generate recurring instances)
```

## Troubleshooting

### "File must have a .ics extension"
- Make sure you selected the iCalendar format when exporting
- Rename the file to end with `.ics` if needed

### "File size must be less than 10MB"
- Your calendar is too large
- Export a smaller date range
- Or split into multiple files

### "Event skipped: missing start or end date"
- Some events in your calendar don't have dates
- These will be skipped automatically
- Check the error details for which events

### Events not appearing correctly
- Check the calendar you selected
- Make sure dates are in the correct timezone
- View job details to see all imported fields

## Tips for Best Results

1. **Export Recent Events**: Export only the date range you need
2. **Check Before Import**: Review your Thunderbird calendar first
3. **Choose Right Calendar**: Select the appropriate target calendar
4. **Start Small**: Try importing a small file first to test
5. **Review After**: Check a few imported jobs to ensure accuracy

## Need Help?

If you encounter issues:
1. Check the error messages on the results page
2. Review the import log in the Django admin
3. Verify your `.ics` file is valid (open in a text editor)
4. Make sure all required fields are present in your events

## Advanced: Understanding Phone Extraction

The system automatically finds phone numbers in these formats:

- `740-501-9004` ✓
- `231-6407` ✓
- `(330) 265-4243` ✓
- `330 265 4243` ✓
- `7405019004` ✓

The phone is removed from the business name automatically!

**Example:**
- Input: `"COLE ALEXANDER 740-501-9004"`
- Business Name: `"COLE ALEXANDER"`
- Phone: `"740-501-9004"`

## Ready to Import!

You now have everything you need to import your Thunderbird calendars into the GTS Scheduler system. Happy importing! 🎉



