# Call Reminder Color Configuration Guide

## Overview
You can customize the color of Call Reminder events that appear on your calendar. Each calendar can have its own Call Reminder color, allowing you to visually distinguish reminders for different calendars.

## How to Change Call Reminder Color

### Step 1: Access Calendar Settings
1. Open the main calendar view
2. Click the **Settings** button in the top-right corner of the calendar toolbar

### Step 2: Select a Calendar to Edit
1. You'll see a list of all your calendars
2. Each calendar displays:
   - Calendar name
   - Calendar color (used for regular job events)
   - **Reminder color** (used for call reminder events)
   - Status (Active/Inactive)
3. Click the **Edit** button next to the calendar you want to modify

### Step 3: Change the Call Reminder Color
1. Scroll down to the **Call Reminder Color** section
2. You have two ways to change the color:
   - **Color Picker**: Click on the colored box to open a visual color picker
   - **Hex Code**: Type or paste a hex color code (e.g., `#F59E0B`)
3. A live preview will show your selected color
4. Click **Update Calendar** to save your changes

## How It Works

### Call Reminders on the Calendar
- When you create a job with a call reminder enabled, two events appear on the calendar:
  1. **Regular Job Event**: Uses the calendar's main color
  2. **Call Reminder Event**: Uses the calendar's call reminder color (appears on the Sunday before the job, based on weeks prior setting)

### Default Color
- The default call reminder color is **#F59E0B** (amber/orange)
- This provides good contrast and visibility on most calendar views

### Per-Calendar Customization
- Each calendar (e.g., "Shop", "Mobile Unit A", "Mobile Unit B") can have its own call reminder color
- This helps you quickly identify which calendar a reminder belongs to

## Quick Access URLs
- **Calendar Settings**: `/calendars/`
- **Edit Specific Calendar**: `/calendars/<id>/edit/`

## Example Use Cases

### Scenario 1: Color-Coding by Priority
- **Shop Calendar**: Use bright red (`#DC2626`) for urgent reminders
- **Mobile Unit A**: Use amber (`#F59E0B`) for standard reminders
- **Mobile Unit B**: Use yellow (`#FBBF24`) for low-priority reminders

### Scenario 2: Team-Based Colors
- **Team 1**: Use blue (`#3B82F6`) for their reminders
- **Team 2**: Use green (`#10B981`) for their reminders
- **Team 3**: Use purple (`#8B5CF6`) for their reminders

## Technical Details

### Color Format
- Colors must be in hex format: `#RRGGBB`
- Example valid colors:
  - `#F59E0B` (amber)
  - `#DC2626` (red)
  - `#3B82F6` (blue)
  - `#10B981` (green)

### Where Colors Are Applied
1. **Calendar List View**: Shows both calendar and reminder colors
2. **Calendar View**: 
   - Regular job events use the calendar color
   - Call reminder events use the call reminder color
3. **Event Details**: The color is visible in the event's visual styling

## Changes Take Effect Immediately
Once you save your color changes, they will be reflected immediately:
- Existing call reminder events will update to the new color
- New call reminder events will use the updated color
- No page refresh required (though you may want to refresh to see changes)

## Tips
1. **High Contrast**: Choose colors that contrast well with white text for readability
2. **Consistent Scheme**: Consider using a consistent color scheme across all your calendars
3. **Accessibility**: Avoid colors that are too similar or hard to distinguish for colorblind users
4. **Test Before Committing**: Try different colors to see what works best in your workflow

## Troubleshooting

### Color Not Updating?
1. Make sure you clicked **Update Calendar** to save changes
2. Refresh the calendar page to see the updated colors
3. Check that the call reminder is not marked as completed (completed reminders may appear differently)

### Can't Find Settings Button?
- The Settings button is located in the top-right corner of the calendar view
- It's next to the "Jobs" button in the calendar toolbar

### Need Help?
If you have questions or need assistance, refer to the main documentation or contact support.







