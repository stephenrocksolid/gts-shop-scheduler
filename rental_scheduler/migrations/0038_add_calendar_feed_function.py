"""
Create the calendar_feed() PostgreSQL function for high-performance calendar event generation.

This function:
1. Filters jobs by date range, calendar, status, search (using GiST index)
2. Expands multi-day jobs into separate day events using generate_series
3. Computes job-linked call reminders (Sunday calculation)
4. Fetches standalone call reminders
5. Returns the complete FullCalendar-compatible JSONB payload in a single query

This replaces the Python-side iteration in get_job_calendar_data() when using PostgreSQL.
"""
from django.db import migrations


CALENDAR_FEED_FUNCTION = """
CREATE OR REPLACE FUNCTION calendar_feed(
    p_req_start date,
    p_req_end date,
    p_calendar_ids int[] DEFAULT NULL,
    p_status text DEFAULT NULL,
    p_search text DEFAULT NULL,
    p_tz text DEFAULT 'America/New_York',
    p_max_expand_days int DEFAULT 365
) RETURNS jsonb
LANGUAGE plpgsql
STABLE
AS $func$
DECLARE
    v_result jsonb;
BEGIN
    WITH 
    -- =========================================================================
    -- 1. Base jobs: filter by is_deleted, calendar, status, search, date overlap
    -- =========================================================================
    base_jobs AS (
        SELECT 
            j.id,
            j.business_name,
            j.contact_name,
            j.phone,
            j.status,
            j.start_dt AT TIME ZONE p_tz AS start_local,
            j.end_dt AT TIME ZONE p_tz AS end_local,
            j.all_day,
            j.trailer_color,
            j.has_call_reminder,
            j.call_reminder_weeks_prior,
            j.call_reminder_completed,
            j.recurrence_rule,
            j.recurrence_parent_id,
            c.id AS calendar_id,
            c.name AS calendar_name,
            c.color AS calendar_color,
            c.call_reminder_color
        FROM rental_scheduler_job j
        JOIN rental_scheduler_calendar c ON j.calendar_id = c.id
        WHERE j.is_deleted = false
          -- Date overlap filter (uses GiST index)
          AND j.start_dt < (p_req_end + interval '1 day') AT TIME ZONE p_tz AT TIME ZONE 'UTC'
          AND j.end_dt >= p_req_start::timestamp AT TIME ZONE p_tz AT TIME ZONE 'UTC'
          -- Calendar filter (optional)
          AND (p_calendar_ids IS NULL OR j.calendar_id = ANY(p_calendar_ids))
          -- Status filter (optional)
          AND (p_status IS NULL OR j.status = p_status)
          -- Search filter (optional, case-insensitive)
          AND (p_search IS NULL OR p_search = '' OR (
              j.business_name ILIKE '%' || p_search || '%' OR
              j.contact_name ILIKE '%' || p_search || '%' OR
              j.phone ILIKE '%' || p_search || '%' OR
              j.trailer_color ILIKE '%' || p_search || '%' OR
              j.trailer_serial ILIKE '%' || p_search || '%' OR
              j.trailer_details ILIKE '%' || p_search || '%' OR
              j.notes ILIKE '%' || p_search || '%' OR
              j.repair_notes ILIKE '%' || p_search || '%'
          ))
    ),
    
    -- =========================================================================
    -- 2. Compute job metadata (title, colors, dates)
    -- =========================================================================
    jobs_with_meta AS (
        SELECT 
            bj.*,
            -- Build title: "Business (Contact) - Phone" or variations
            CASE 
                WHEN bj.business_name != '' AND bj.contact_name != '' THEN
                    bj.business_name || ' (' || bj.contact_name || ')' ||
                    CASE WHEN bj.phone != '' THEN ' - ' || bj.phone ELSE '' END
                WHEN bj.business_name != '' THEN
                    bj.business_name ||
                    CASE WHEN bj.phone != '' THEN ' - ' || bj.phone ELSE '' END
                WHEN bj.contact_name != '' THEN
                    bj.contact_name ||
                    CASE WHEN bj.phone != '' THEN ' - ' || bj.phone ELSE '' END
                ELSE
                    'No Name Provided' ||
                    CASE WHEN bj.phone != '' THEN ' - ' || bj.phone ELSE '' END
            END AS title,
            -- Display name (for extendedProps)
            COALESCE(NULLIF(bj.business_name, ''), NULLIF(bj.contact_name, ''), 'No Name Provided') AS display_name,
            -- Effective color (lighter for completed)
            CASE 
                WHEN bj.status = 'completed' THEN 
                    -- Lighten by 30%: blend with white
                    '#' || 
                    lpad(to_hex(least(255, (('x' || substr(bj.calendar_color, 2, 2))::bit(8)::int + (255 - ('x' || substr(bj.calendar_color, 2, 2))::bit(8)::int) * 3 / 10)::int)), 2, '0') ||
                    lpad(to_hex(least(255, (('x' || substr(bj.calendar_color, 4, 2))::bit(8)::int + (255 - ('x' || substr(bj.calendar_color, 4, 2))::bit(8)::int) * 3 / 10)::int)), 2, '0') ||
                    lpad(to_hex(least(255, (('x' || substr(bj.calendar_color, 6, 2))::bit(8)::int + (255 - ('x' || substr(bj.calendar_color, 6, 2))::bit(8)::int) * 3 / 10)::int)), 2, '0')
                ELSE bj.calendar_color
            END AS effective_color,
            -- Job date boundaries
            (bj.start_local)::date AS job_start_date,
            (bj.end_local)::date AS job_end_date,
            -- Is multi-day?
            ((bj.end_local)::date > (bj.start_local)::date) AS is_multi_day,
            -- Recurring flags (use ID to avoid loading related object)
            (bj.recurrence_rule IS NOT NULL AND bj.recurrence_parent_id IS NULL) AS is_recurring_parent,
            (bj.recurrence_parent_id IS NOT NULL) AS is_recurring_instance
        FROM base_jobs bj
    ),
    
    -- =========================================================================
    -- 3. Expand multi-day jobs using generate_series
    -- =========================================================================
    expanded_days AS (
        SELECT 
            jm.*,
            gs.day_date,
            -- Day number within the job (0-indexed)
            (gs.day_date - jm.job_start_date) AS day_number,
            -- Total days in job
            (jm.job_end_date - jm.job_start_date) AS total_days
        FROM jobs_with_meta jm
        CROSS JOIN LATERAL (
            SELECT generate_series(
                GREATEST(jm.job_start_date, p_req_start),
                LEAST(
                    jm.job_end_date, 
                    p_req_end,
                    GREATEST(jm.job_start_date, p_req_start) + p_max_expand_days
                ),
                interval '1 day'
            )::date AS day_date
        ) gs
        WHERE jm.is_multi_day
        
        UNION ALL
        
        -- Single-day jobs (no expansion needed)
        SELECT 
            jm.*,
            jm.job_start_date AS day_date,
            0 AS day_number,
            0 AS total_days
        FROM jobs_with_meta jm
        WHERE NOT jm.is_multi_day
    ),
    
    -- =========================================================================
    -- 4. Build job events with proper start/end times
    -- =========================================================================
    job_events AS (
        SELECT jsonb_build_object(
            'id', CASE 
                WHEN ed.is_multi_day THEN 'job-' || ed.id || '-day-' || ed.day_number
                ELSE 'job-' || ed.id
            END,
            'title', ed.title,
            'start', CASE
                -- All-day events: use noon to avoid timezone shifting
                WHEN ed.all_day THEN to_char(ed.day_date, 'YYYY-MM-DD') || 'T12:00:00'
                -- First day of multi-day: start at job time
                WHEN ed.is_multi_day AND ed.day_date = ed.job_start_date THEN 
                    to_char(ed.start_local, 'YYYY-MM-DD"T"HH24:MI:SS')
                -- Middle/last days: start at midnight
                WHEN ed.is_multi_day THEN 
                    to_char(ed.day_date, 'YYYY-MM-DD') || 'T00:00:00'
                -- Single-day timed event
                ELSE to_char(ed.start_local, 'YYYY-MM-DD"T"HH24:MI:SS')
            END,
            'end', CASE
                -- All-day events: next day noon (exclusive end)
                WHEN ed.all_day THEN to_char(ed.day_date + 1, 'YYYY-MM-DD') || 'T12:00:00'
                -- Last day of multi-day: end at job time
                WHEN ed.is_multi_day AND ed.day_date = ed.job_end_date THEN 
                    to_char(ed.end_local, 'YYYY-MM-DD"T"HH24:MI:SS')
                -- First/middle days: end at next midnight
                WHEN ed.is_multi_day THEN 
                    to_char(ed.day_date + 1, 'YYYY-MM-DD') || 'T00:00:00'
                -- Single-day timed event
                ELSE to_char(ed.end_local, 'YYYY-MM-DD"T"HH24:MI:SS')
            END,
            'allDay', ed.all_day,
            'backgroundColor', ed.effective_color,
            'borderColor', ed.effective_color,
            'extendedProps', jsonb_build_object(
                'type', 'job',
                'job_id', ed.id,
                'status', ed.status,
                'calendar_id', ed.calendar_id,
                'calendar_name', ed.calendar_name,
                'display_name', ed.display_name,
                'phone', ed.phone,
                'trailer_color', ed.trailer_color,
                'is_recurring_parent', ed.is_recurring_parent,
                'is_recurring_instance', ed.is_recurring_instance,
                'is_multi_day', ed.is_multi_day,
                'multi_day_number', CASE WHEN ed.is_multi_day THEN ed.day_number ELSE null END,
                'multi_day_total', CASE WHEN ed.is_multi_day THEN ed.total_days ELSE null END,
                'job_start_date', CASE WHEN ed.is_multi_day THEN to_char(ed.job_start_date, 'YYYY-MM-DD') ELSE null END,
                'job_end_date', CASE WHEN ed.is_multi_day THEN to_char(ed.job_end_date, 'YYYY-MM-DD') ELSE null END
            )
        ) AS event_json
        FROM expanded_days ed
    ),
    
    -- =========================================================================
    -- 5. Job-linked call reminders
    -- =========================================================================
    job_call_reminders AS (
        SELECT jsonb_build_object(
            'id', 'reminder-' || jm.id,
            'title', '📞 ' || jm.title,
            'start', to_char(reminder_sunday, 'YYYY-MM-DD') || 'T12:00:00',
            'end', to_char(reminder_sunday + 1, 'YYYY-MM-DD') || 'T12:00:00',
            'allDay', true,
            'backgroundColor', jm.call_reminder_color,
            'borderColor', jm.call_reminder_color,
            'extendedProps', jsonb_build_object(
                'type', 'call_reminder',
                'job_id', jm.id,
                'status', jm.status,
                'calendar_id', jm.calendar_id,
                'calendar_name', jm.calendar_name,
                'business_name', jm.business_name,
                'contact_name', jm.contact_name,
                'phone', jm.phone,
                'weeks_prior', jm.call_reminder_weeks_prior,
                'job_date', to_char(jm.job_start_date, 'YYYY-MM-DD'),
                'call_reminder_completed', jm.call_reminder_completed,
                'notes_preview', COALESCE(
                    (SELECT CASE WHEN length(cr.notes) > 50 THEN substr(cr.notes, 1, 50) || '...' ELSE cr.notes END
                     FROM rental_scheduler_callreminder cr WHERE cr.job_id = jm.id LIMIT 1),
                    ''
                ),
                'has_notes', EXISTS (
                    SELECT 1 FROM rental_scheduler_callreminder cr 
                    WHERE cr.job_id = jm.id AND cr.notes IS NOT NULL AND cr.notes != ''
                )
            )
        ) AS event_json
        FROM jobs_with_meta jm
        CROSS JOIN LATERAL (
            -- Calculate reminder Sunday: job_week_sunday - (weeks_prior - 1) * 7 days
            -- job_week_sunday = job_date - day_of_week (where Sunday = 0)
            SELECT (
                jm.job_start_date 
                - EXTRACT(DOW FROM jm.job_start_date)::int 
                - ((jm.call_reminder_weeks_prior - 1) * 7)
            )::date AS reminder_sunday
        ) rs
        WHERE jm.has_call_reminder 
          AND jm.call_reminder_weeks_prior IS NOT NULL
          AND NOT jm.call_reminder_completed
          -- Only include if reminder falls within request window
          AND rs.reminder_sunday >= p_req_start
          AND rs.reminder_sunday <= p_req_end
    ),
    
    -- =========================================================================
    -- 6. Standalone call reminders (not linked to jobs)
    -- =========================================================================
    standalone_reminders AS (
        SELECT jsonb_build_object(
            'id', 'call-reminder-' || cr.id,
            'title', CASE 
                WHEN cr.completed THEN '✓ 📞 ' 
                ELSE '📞 ' 
            END || CASE 
                WHEN cr.notes IS NOT NULL AND cr.notes != '' THEN
                    CASE WHEN length(cr.notes) > 50 THEN substr(cr.notes, 1, 50) || '...' ELSE cr.notes END
                ELSE 'Call Reminder'
            END,
            'start', to_char(cr.reminder_date, 'YYYY-MM-DD') || 'T12:00:00',
            'end', to_char(cr.reminder_date + 1, 'YYYY-MM-DD') || 'T12:00:00',
            'allDay', true,
            'backgroundColor', CASE 
                WHEN cr.completed THEN 
                    -- Lighten completed reminders
                    '#' || 
                    lpad(to_hex(least(255, (('x' || substr(c.call_reminder_color, 2, 2))::bit(8)::int + (255 - ('x' || substr(c.call_reminder_color, 2, 2))::bit(8)::int) * 3 / 10)::int)), 2, '0') ||
                    lpad(to_hex(least(255, (('x' || substr(c.call_reminder_color, 4, 2))::bit(8)::int + (255 - ('x' || substr(c.call_reminder_color, 4, 2))::bit(8)::int) * 3 / 10)::int)), 2, '0') ||
                    lpad(to_hex(least(255, (('x' || substr(c.call_reminder_color, 6, 2))::bit(8)::int + (255 - ('x' || substr(c.call_reminder_color, 6, 2))::bit(8)::int) * 3 / 10)::int)), 2, '0')
                ELSE c.call_reminder_color
            END,
            'borderColor', CASE 
                WHEN cr.completed THEN 
                    '#' || 
                    lpad(to_hex(least(255, (('x' || substr(c.call_reminder_color, 2, 2))::bit(8)::int + (255 - ('x' || substr(c.call_reminder_color, 2, 2))::bit(8)::int) * 3 / 10)::int)), 2, '0') ||
                    lpad(to_hex(least(255, (('x' || substr(c.call_reminder_color, 4, 2))::bit(8)::int + (255 - ('x' || substr(c.call_reminder_color, 4, 2))::bit(8)::int) * 3 / 10)::int)), 2, '0') ||
                    lpad(to_hex(least(255, (('x' || substr(c.call_reminder_color, 6, 2))::bit(8)::int + (255 - ('x' || substr(c.call_reminder_color, 6, 2))::bit(8)::int) * 3 / 10)::int)), 2, '0')
                ELSE c.call_reminder_color
            END,
            'extendedProps', jsonb_build_object(
                'type', 'standalone_call_reminder',
                'reminder_id', cr.id,
                'calendar_id', c.id,
                'calendar_name', c.name,
                'notes_preview', CASE 
                    WHEN cr.notes IS NOT NULL AND cr.notes != '' THEN
                        CASE WHEN length(cr.notes) > 50 THEN substr(cr.notes, 1, 50) || '...' ELSE cr.notes END
                    ELSE ''
                END,
                'has_notes', (cr.notes IS NOT NULL AND cr.notes != ''),
                'completed', cr.completed,
                'reminder_date', to_char(cr.reminder_date, 'YYYY-MM-DD')
            )
        ) AS event_json
        FROM rental_scheduler_callreminder cr
        JOIN rental_scheduler_calendar c ON cr.calendar_id = c.id
        WHERE cr.job_id IS NULL
          AND cr.reminder_date >= p_req_start
          AND cr.reminder_date <= p_req_end
          AND (p_calendar_ids IS NULL OR cr.calendar_id = ANY(p_calendar_ids))
          AND c.is_active = true
    ),
    
    -- =========================================================================
    -- 7. Combine all events
    -- =========================================================================
    all_events AS (
        SELECT event_json FROM job_events
        UNION ALL
        SELECT event_json FROM job_call_reminders
        UNION ALL
        SELECT event_json FROM standalone_reminders
    )
    
    -- Return as JSONB array
    SELECT COALESCE(jsonb_agg(event_json), '[]'::jsonb)
    INTO v_result
    FROM all_events;
    
    RETURN v_result;
END;
$func$;
"""

DROP_CALENDAR_FEED_FUNCTION = "DROP FUNCTION IF EXISTS calendar_feed(date, date, int[], text, text, text, int);"


class Migration(migrations.Migration):

    dependencies = [
        ('rental_scheduler', '0037_add_postgres_gist_indexes'),
    ]

    operations = [
        migrations.RunSQL(
            sql=CALENDAR_FEED_FUNCTION,
            reverse_sql=DROP_CALENDAR_FEED_FUNCTION,
            state_operations=[],
        ),
    ]
