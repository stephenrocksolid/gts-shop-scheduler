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
