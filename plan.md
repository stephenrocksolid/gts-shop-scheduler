### Fix Timezone Discrepancy for Contract Return Times

Problem: Actual return times are displayed several hours off in the Availability UI (e.g., 07:46 AM vs. 11:46 AM) due to UTC↔local timezone mismatches.

#### Goals
1. Store all datetimes in UTC in the database (Django default with `USE_TZ = True`).
2. Display all datetimes in the tenant’s local timezone (configured in `settings.TIME_ZONE`).
3. Preserve accurate comparisons when determining availability/overdue status.

#### Implementation Plan

1. Reproduce & Investigate
   1.1. Create a sample contract with known local start/return times.
   1.2. Observe values in DB (`psql` / Django shell) and Availability UI to quantify the offset.
   1.3. Capture failing scenario in an integration test (`test_contract_integration`).

2. Audit Project Time-Zone Settings
   2.1. Verify `USE_TZ = True`.
   2.2. Verify `TIME_ZONE = 'America/New_York'` (or correct local zone).
   2.3. Ensure no third-party libs override these settings.

3. Trace Datetime Flow
   3.1. Models: confirm `start_datetime`, `end_datetime`, `return_datetime` are timezone-aware `DateTimeField`.
   3.2. Availability pipeline:
        • `services/availability.is_trailer_available`
        • `views.availability_search` (lines ~2560-2600)
        • `templates/partials/unavailability_results.html`
   3.3. Identify every `.strftime` / manual formatting call.

4. Backend Fixes
   4.1. Create utility helper `utils/datetime.py` with:
```
from django.utils import timezone

def to_local(dt):
    if dt is None:
        return None
    return timezone.localtime(dt)
```
   4.2. Add custom template filter `local_dt` in `templatetags/datetime_tags.py` to format dates safely.
   4.3. Replace all occurrences of:
        `dt.strftime('%m/%d/%Y %I:%M %p')`
        with:
        `to_local(dt).strftime('%m/%d/%Y %I:%M %p')`
   4.4. When serialising to the front-end (`return_iso`), send:
        `to_local(dt).isoformat()` so JS receives local time.

5. Front-End Fixes
   5.1. Ensure Flatpickr initialization doesn’t apply additional timezone shifts (set `time_24hr` + `utc: false`).
   5.2. Where we read `data-return-iso`, rely on browser-parsed local ISO string.

6. Update Availability Logic (if needed)
   6.1. For comparisons inside `is_trailer_available` & `availability_search`, ensure `start_datetime`, `end_datetime`, and `now` are all timezone-aware (already are) and in UTC; `timezone.now()` suffices.

7. Testing
   7.1. Extend `test_contract_integration.py` to assert displayed times match expected local times.
   7.2. Add unit tests for `to_local` helper & `local_dt` filter.
   7.3. Run full test suite.

8. Documentation & Deployment
   8.1. Update `README.md` with timezone policy.
   8.2. Record the above steps and rationale in `plan.md` (this document) and append summary to `roadmap.md`.
   8.3. Deploy; verify UI shows correct times.

#### Rollback Plan
If issues arise, revert commits related to timezone conversion and disable template filter usage pending further investigation.

---
