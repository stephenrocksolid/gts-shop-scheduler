"""
Add PostgreSQL-specific GiST range indexes for fast calendar overlap queries.

This migration:
1. Enables the btree_gist extension (required for composite GiST indexes with integers)
2. Creates a GiST index on (calendar_id, tstzrange(start_dt, end_dt)) for fast overlap filtering
3. Creates a GiST index for standalone CallReminders

These indexes are Postgres-only and significantly speed up the calendar feed query.
The migration is a no-op on SQLite (safe to run on any backend).
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rental_scheduler', '0036_add_calendar_performance_indexes'),
    ]

    operations = [
        # Enable btree_gist extension (required for composite GiST with integers)
        # This is a no-op if already enabled
        migrations.RunSQL(
            sql="CREATE EXTENSION IF NOT EXISTS btree_gist;",
            reverse_sql="DROP EXTENSION IF EXISTS btree_gist;",
            # Only run on PostgreSQL
            state_operations=[],
        ),
        
        # GiST range index for fast job overlap queries
        # This covers the calendar feed's primary filter:
        #   WHERE is_deleted = false AND start_dt < :end AND end_dt >= :start
        # Using tstzrange with && (overlaps) operator is faster than separate comparisons
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS job_active_range_gist_idx
                ON rental_scheduler_job
                USING gist (calendar_id, tstzrange(start_dt, end_dt, '[]'))
                WHERE is_deleted = false;
            """,
            reverse_sql="DROP INDEX IF EXISTS job_active_range_gist_idx;",
            state_operations=[],
        ),
        
        # Alternative: simple GiST on just the time range (useful if filtering by calendar separately)
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS job_active_timerange_gist_idx
                ON rental_scheduler_job
                USING gist (tstzrange(start_dt, end_dt, '[]'))
                WHERE is_deleted = false;
            """,
            reverse_sql="DROP INDEX IF EXISTS job_active_timerange_gist_idx;",
            state_operations=[],
        ),
        
        # Index for call reminder notes subquery (job_id lookups)
        # Already covered by Django model indexes, but ensure it exists
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS callreminder_job_notes_idx
                ON rental_scheduler_callreminder (job_id)
                WHERE job_id IS NOT NULL;
            """,
            reverse_sql="DROP INDEX IF EXISTS callreminder_job_notes_idx;",
            state_operations=[],
        ),
    ]
