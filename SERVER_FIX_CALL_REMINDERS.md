# Fix for Call Reminder 500 Error on Server

## Problem
On the production server (192.168.1.205), call reminders cannot be created due to a 500 error. This is caused by corrupted data in the database where `reminder_date` fields may have been stored as datetime values instead of date values.

## Symptoms
- Call reminders work fine on local development
- Server shows error: `"2025-10-19T00:00:00-06:00" value has an invalid date format. It must be in YYYY-MM-DD format.`
- Calendar view may fail to load standalone call reminders

## Solution Overview
The fix includes:
1. A defensive code change to handle corrupted data gracefully
2. A data migration to fix existing corrupted records
3. A management command for manual cleanup if needed

## Deployment Steps for Server

### Step 1: Deploy the Code Changes
Transfer these updated files to your server:
- `rental_scheduler/views.py` (defensive code added)
- `rental_scheduler/migrations/0029_fix_call_reminder_dates.py` (data migration)
- `rental_scheduler/management/commands/fix_call_reminder_dates.py` (cleanup command)

### Step 2: Run Migrations
On the server, run:
```bash
python manage.py migrate
```

This will automatically fix any corrupted `reminder_date` fields in the database.

### Step 3: (Optional) Manual Cleanup Command
If the migration doesn't resolve all issues, you can run the manual cleanup command:
```bash
python manage.py fix_call_reminder_dates
```

This will:
- Check all CallReminder records
- Convert any datetime values to date values
- Show you a summary of what was fixed
- Display the current database schema

### Step 4: Restart the Server
Restart your Django application server (Gunicorn/uWSGI/etc.) to ensure all code changes are loaded.

### Step 5: Test
1. Navigate to the calendar view
2. Try creating a new call reminder
3. Verify that existing call reminders display correctly
4. Check that the 500 error no longer occurs

## What Was Changed

### 1. `rental_scheduler/views.py`
- Added defensive code in `get_job_calendar_data()` to detect and fix datetime values in date fields
- Each call reminder is now processed individually with error handling
- If a corrupted record is found, it's automatically fixed in the database

### 2. Data Migration
- `0029_fix_call_reminder_dates.py` scans all CallReminder records on migration
- Converts any datetime values to date values
- Runs automatically when you execute `python manage.py migrate`

### 3. Management Command
- `fix_call_reminder_dates` provides a manual way to fix records
- Useful for troubleshooting or if you need to run the fix again
- Shows detailed output about what was fixed

## Verification

After deploying, check the server logs to confirm:
```bash
tail -f logs/gts_scheduler.log
```

You should see:
- No more "invalid date format" errors
- Call reminders being created successfully
- Calendar view loading without errors

## Rollback (if needed)
If something goes wrong:
1. The code changes are defensive and won't break anything
2. The data migration only converts datetime to date (safe operation)
3. You can restore from a database backup if needed

## Root Cause
The issue likely occurred due to:
- Direct database manipulation that bypassed Django's ORM
- A previous bug in the code that has since been fixed
- Database import/export that didn't preserve field types correctly

## Prevention
Going forward:
- Always use Django's ORM for database operations
- Run migrations after any code changes
- Test migrations on a copy of production data before deploying








