"""
Centralized availability logic for trailers
"""
from django.utils import timezone
import logging
logger = logging.getLogger(__name__)
from django.db.models import Q


def _blocking_contracts_q(start_datetime, end_datetime):
    returned_overlap = Q(
        is_returned=True,
        start_datetime__lt=end_datetime,
        return_datetime__gt=start_datetime,
    )
    not_returned_overlap = Q(
        is_returned=False,
        start_datetime__lt=end_datetime,
        end_datetime__gt=start_datetime,
    )
    return returned_overlap | not_returned_overlap


def is_trailer_available(trailer, start_datetime, end_datetime, exclude_contract_id=None):
    """
    Check if a trailer is available for rental during a specific time period.
    
    Args:
        trailer: Trailer instance to check availability for
        start_datetime: Start of the requested rental period
        end_datetime: End of the requested rental period  
        exclude_contract_id: Optional contract ID to exclude from overlap check (for editing)
        
    Returns:
        tuple: (is_available: bool, reason: str or None)
        
    Reasons for unavailability:
        - "not_active": Trailer is marked as not available
        - "under_service": Trailer is under service/maintenance
        - "booked": Trailer has overlapping rental contract
    """
    logger.info(
        f"is_trailer_available: trailer={getattr(trailer, 'id', None)} "
        f"start={start_datetime} tz={getattr(start_datetime, 'tzinfo', None)} "
        f"end={end_datetime} tz={getattr(end_datetime, 'tzinfo', None)} "
        f"exclude_contract_id={exclude_contract_id}"
    )

    if not trailer.is_available:
        return False, "not_active"
    
    from rental_scheduler.models import TrailerService
    service_overlap = TrailerService.objects.filter(
        trailer=trailer,
        start_datetime__lt=end_datetime,
        end_datetime__gt=start_datetime
    ).exists()
    
    if service_overlap:
        logger.warning("is_trailer_available: under_service overlap detected")
        return False, "under_service"
    
    from rental_scheduler.models import Contract
    contract_query = Contract.objects.filter(trailer=trailer).filter(
        _blocking_contracts_q(start_datetime, end_datetime)
    )
    logger.info(
        "is_trailer_available: initial blocking contracts count=%s details=%s",
        contract_query.count(),
        list(
            contract_query.values(
                "id", "start_datetime", "end_datetime", "is_returned", "return_datetime"
            )
        )
    )

    if exclude_contract_id:
        contract_query = contract_query.exclude(id=exclude_contract_id)
        logger.info(
            "is_trailer_available: after exclude id=%s count=%s details=%s",
            exclude_contract_id,
            contract_query.count(),
            list(
                contract_query.values(
                    "id", "start_datetime", "end_datetime", "is_returned", "return_datetime"
                )
            )
        )
    
    if contract_query.exists():
        logger.warning(
            "is_trailer_available: booked due to contracts=%s",
            list(contract_query.values_list("id", flat=True))
        )
        return False, "booked"
    
    return True, None


def get_available_trailers_for_period(category_id=None, start_datetime=None, end_datetime=None, exclude_contract_id=None):
    """
    Get all trailers available for a specific time period.
    
    Args:
        category_id: Optional category filter
        start_datetime: Start of the requested rental period
        end_datetime: End of the requested rental period
        exclude_contract_id: Optional contract ID to exclude from overlap check
        
    Returns:
        QuerySet: Available trailers
    """
    from rental_scheduler.models import Trailer
    
    # Base query for active trailers
    trailers_query = Trailer.objects.filter(is_available=True)
    
    # Filter by category if specified
    if category_id:
        trailers_query = trailers_query.filter(category_id=category_id)
    
    # If no date range specified, return all active trailers sorted by size
    if not start_datetime or not end_datetime:
        return trailers_query.order_by('length', 'width', 'number')
    
    # Get trailers that are NOT under service during the period
    from rental_scheduler.models import TrailerService
    service_excluded_trailer_ids = TrailerService.objects.filter(
        start_datetime__lt=end_datetime,
        end_datetime__gt=start_datetime
    ).values_list('trailer_id', flat=True)
    
    trailers_query = trailers_query.exclude(id__in=service_excluded_trailer_ids)
    
    # Get trailers that are NOT booked during the period
    from rental_scheduler.models import Contract
    contract_exclusion_query = Contract.objects.filter(
        _blocking_contracts_q(start_datetime, end_datetime)
    )
    
    # Exclude current contract if editing
    if exclude_contract_id:
        contract_exclusion_query = contract_exclusion_query.exclude(id=exclude_contract_id)
    
    booked_trailer_ids = contract_exclusion_query.values_list('trailer_id', flat=True)
    trailers_query = trailers_query.exclude(id__in=booked_trailer_ids)
    
    return trailers_query.order_by('length', 'width', 'number') 