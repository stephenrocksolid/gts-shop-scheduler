"""
Centralized constants for rental_scheduler application.

This module is the single source of truth for validation thresholds,
API safety caps, and UX warning limits. Both server-side Python code
and client-side JavaScript (via window.calendarConfig.guardrails)
should use these values.
"""

# =============================================================================
# HARD VALIDATION LIMITS (Server-side authoritative)
# These are enforced in models.py, forms.py, and API endpoints.
# Violations result in validation errors.
# =============================================================================

MIN_VALID_YEAR = 2000
"""Minimum acceptable year for job dates. Prevents typos like '0026'."""

MAX_VALID_YEAR = 2100
"""Maximum acceptable year for job dates. Prevents far-future mistakes."""

MAX_JOB_SPAN_DAYS = 365
"""Maximum number of days a single job can span. Prevents runaway multi-day expansion."""


# =============================================================================
# API SAFETY CAPS
# These prevent runaway responses even if validation is somehow bypassed.
# =============================================================================

MAX_MULTI_DAY_EXPANSION_DAYS = 120
"""Maximum days to expand for multi-day job events in calendar API response."""


# =============================================================================
# UX WARNING THRESHOLDS (Client-side prompts)
# These trigger "are you sure?" confirmations in the UI but don't block saves.
# Intentionally more conservative than hard limits.
# =============================================================================

WARN_DAYS_IN_FUTURE = 1095
"""Warn user if scheduling more than this many days (3 years) in the future."""

WARN_DAYS_IN_PAST = 30
"""Warn user if scheduling more than this many days in the past (new jobs only)."""

WARN_JOB_SPAN_DAYS = 60
"""Warn user if job spans more than this many days."""


# =============================================================================
# US STATE AND TERRITORY CODES
# Used for customer address validation in Work Orders.
# =============================================================================

US_STATE_TERRITORY_CHOICES = [
    ("AL", "Alabama"),
    ("AK", "Alaska"),
    ("AZ", "Arizona"),
    ("AR", "Arkansas"),
    ("CA", "California"),
    ("CO", "Colorado"),
    ("CT", "Connecticut"),
    ("DE", "Delaware"),
    ("DC", "District of Columbia"),
    ("FL", "Florida"),
    ("GA", "Georgia"),
    ("HI", "Hawaii"),
    ("ID", "Idaho"),
    ("IL", "Illinois"),
    ("IN", "Indiana"),
    ("IA", "Iowa"),
    ("KS", "Kansas"),
    ("KY", "Kentucky"),
    ("LA", "Louisiana"),
    ("ME", "Maine"),
    ("MD", "Maryland"),
    ("MA", "Massachusetts"),
    ("MI", "Michigan"),
    ("MN", "Minnesota"),
    ("MS", "Mississippi"),
    ("MO", "Missouri"),
    ("MT", "Montana"),
    ("NE", "Nebraska"),
    ("NV", "Nevada"),
    ("NH", "New Hampshire"),
    ("NJ", "New Jersey"),
    ("NM", "New Mexico"),
    ("NY", "New York"),
    ("NC", "North Carolina"),
    ("ND", "North Dakota"),
    ("OH", "Ohio"),
    ("OK", "Oklahoma"),
    ("OR", "Oregon"),
    ("PA", "Pennsylvania"),
    ("RI", "Rhode Island"),
    ("SC", "South Carolina"),
    ("SD", "South Dakota"),
    ("TN", "Tennessee"),
    ("TX", "Texas"),
    ("UT", "Utah"),
    ("VT", "Vermont"),
    ("VA", "Virginia"),
    ("WA", "Washington"),
    ("WV", "West Virginia"),
    ("WI", "Wisconsin"),
    ("WY", "Wyoming"),
    # US Territories
    ("AS", "American Samoa"),
    ("GU", "Guam"),
    ("MP", "Northern Mariana Islands"),
    ("PR", "Puerto Rico"),
    ("VI", "U.S. Virgin Islands"),
]
"""List of (code, name) tuples for US states and territories. Used in Work Order customer modal."""

US_STATE_TERRITORY_CODE_SET = {code for code, _ in US_STATE_TERRITORY_CHOICES}
"""Set of valid 2-letter USPS state/territory codes for fast validation."""

# Optional: name → code mapping for defensive normalization
US_STATE_TERRITORY_NAME_TO_CODE = {name.upper(): code for code, name in US_STATE_TERRITORY_CHOICES}
"""Mapping of uppercase state/territory names to 2-letter codes (e.g., 'TENNESSEE' → 'TN')."""


# =============================================================================
# HELPER: Get guardrails dict for frontend
# =============================================================================

def get_guardrails_for_frontend():
    """
    Returns a dict of guardrails to be serialized as JSON and exposed
    to the frontend via window.calendarConfig.guardrails.
    
    Uses camelCase keys to match JavaScript conventions.
    """
    return {
        # Hard validation limits (for UI error messages)
        'minValidYear': MIN_VALID_YEAR,
        'maxValidYear': MAX_VALID_YEAR,
        'maxJobSpanDays': MAX_JOB_SPAN_DAYS,
        # UX warning thresholds (for confirmation prompts)
        'warnDaysInFuture': WARN_DAYS_IN_FUTURE,
        'warnDaysInPast': WARN_DAYS_IN_PAST,
        'warnJobSpanDays': WARN_JOB_SPAN_DAYS,
    }
