"""
Centralized rental calculation service.
Single source of truth for all rental pricing and duration calculations.
"""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, Optional, Tuple
import math


class RentalCalculator:
    """
    Centralized service for all rental calculations.
    This is the single source of truth for business rules.
    """
    
    # Business Rule Constants - Single Source of Truth
    HALF_DAY_HOURS = 5
    HALF_DAY_THRESHOLD = Decimal(str(HALF_DAY_HOURS)) / Decimal('24')  # 0.208333...
    
    # Rate calculation thresholds
    DAILY_RATE_MAX_DAYS = 4
    WEEKLY_RATE_MAX_DAYS = 7
    WEEKLY_RATE_DIVISOR = 6  # For extended rentals (weekly_rate / 6)
    
    @staticmethod
    def calculate_duration_info(start_datetime: datetime, end_datetime: datetime) -> Dict[str, Any]:
        """
        Calculate comprehensive duration information.
        
        Args:
            start_datetime: Rental start date/time
            end_datetime: Rental end date/time
            
        Returns:
            Dict containing:
            - days: Duration in decimal days
            - hours: Total hours
            - days_display: Formatted display string
            - is_half_day: Whether this qualifies as half day
            - rate_category: 'half_day', 'daily', 'weekly', or 'extended'
            - full_days: Number of complete days
            - has_half_day: Whether remainder qualifies as half-day increment
            - remainder: Fractional day portion after full days
        """
        if end_datetime <= start_datetime:
            raise ValueError("End date/time must be after start date/time")
            
        duration = end_datetime - start_datetime
        total_seconds = duration.total_seconds()
        total_hours = total_seconds / 3600
        total_days = Decimal(str(total_seconds)) / Decimal('86400')  # Use Decimal for precision
        
        # Calculate full days and remainder for new pricing model
        full_days = int(total_days)
        remainder = float(total_days) - full_days
        
        # Determine if remainder qualifies as half-day
        remainder_decimal = Decimal(str(remainder))
        remainder_quantized = remainder_decimal.quantize(Decimal('0.000000001'))
        threshold = RentalCalculator.HALF_DAY_THRESHOLD.quantize(Decimal('0.000000001'))
        has_half_day = remainder > 0 and remainder_quantized <= threshold
        
        # Determine rate category
        is_half_day = total_days <= RentalCalculator.HALF_DAY_THRESHOLD
        max_daily_with_half = RentalCalculator.DAILY_RATE_MAX_DAYS + 0.5
        
        if is_half_day:
            rate_category = 'half_day'
        elif float(total_days) <= max_daily_with_half:
            rate_category = 'daily'
        elif float(total_days) <= RentalCalculator.WEEKLY_RATE_MAX_DAYS:
            rate_category = 'weekly'
        else:
            rate_category = 'extended'
            
        # Format display string - use centralized format_duration_display for consistency
        # This is kept for backward compatibility but format_duration_display is preferred
        days_whole = int(total_days)
        hours_remainder = int((total_days - days_whole) * 24)
        
        if days_whole > 0:
            days_display = f"{days_whole} day{'s' if days_whole != 1 else ''}"
            if hours_remainder > 0:
                days_display += f" {hours_remainder} hour{'s' if hours_remainder != 1 else ''}"
        else:
            # For sub-day rentals, show hours for clarity
            days_display = f"{int(total_hours)} hour{'s' if int(total_hours) != 1 else ''}"
            
        return {
            'days': float(total_days),
            'hours': total_hours,
            'days_display': days_display,
            'is_half_day': is_half_day,
            'rate_category': rate_category,
            'full_days': full_days,
            'has_half_day': has_half_day,
            'remainder': remainder,
            'total_seconds': total_seconds,
            'start_datetime': start_datetime,
            'end_datetime': end_datetime
        }
    
    @staticmethod
    def calculate_base_rate(trailer, duration_days: float, custom_rate: Optional[Decimal] = None) -> Decimal:
        """
        Calculate base rental rate using business rules.
        
        Supports half-day increments after full days (e.g., 1.5, 2.5, 3.5, 4.5 days).
        
        Args:
            trailer: Trailer object with rate fields
            duration_days: Duration in decimal days
            custom_rate: Optional custom rate override
            
        Returns:
            Calculated rate as Decimal
        """
        if custom_rate is not None:
            return Decimal(str(custom_rate))
            
        duration_decimal = Decimal(str(duration_days))
        
        # Apply business rules with small epsilon for floating point precision
        # Use quantize to ensure same precision for comparison
        threshold = RentalCalculator.HALF_DAY_THRESHOLD.quantize(Decimal('0.000000001'))
        duration_quantized = duration_decimal.quantize(Decimal('0.000000001'))
        
        # Pure half-day rental (≤ 5 hours)
        if duration_quantized <= threshold:
            return trailer.half_day_rate
        
        # Calculate full days and remainder
        full_days = int(duration_days)
        remainder = duration_days - full_days
        
        # Determine if we're in daily rate territory (up to 4.5 days)
        max_daily_with_half = RentalCalculator.DAILY_RATE_MAX_DAYS + 0.5
        
        if duration_days <= max_daily_with_half:
            # Daily rate territory: full days + optional half-day
            base_cost = trailer.daily_rate * full_days
            
            # Add half-day rate if remainder qualifies as half-day
            if remainder > 0:
                remainder_decimal = Decimal(str(remainder))
                remainder_quantized = remainder_decimal.quantize(Decimal('0.000000001'))
                
                if remainder_quantized <= threshold:
                    base_cost += trailer.half_day_rate
                else:
                    # Remainder is more than half-day, charge another full day
                    base_cost += trailer.daily_rate
                    
            return base_cost
            
        # Round up to nearest full day for weekly/extended calculations
        days_ceil = math.ceil(duration_days)
        
        if days_ceil <= RentalCalculator.WEEKLY_RATE_MAX_DAYS:
            return trailer.weekly_rate
        else:
            # Extended rental: (weekly_rate / 6) * days
            daily_rate = trailer.weekly_rate / RentalCalculator.WEEKLY_RATE_DIVISOR
            return daily_rate * days_ceil
    
    @staticmethod
    def calculate_addon_costs(
        settings,
        includes_winch: bool = False,
        includes_hitch_bar: bool = False,
        furniture_blanket_count: int = 0,
        strap_chain_count: int = 0,
        has_evening_pickup: bool = False
    ) -> Dict[str, Decimal]:
        """
        Calculate all addon costs.
        
        Args:
            settings: SystemSettings object
            includes_winch: Whether rental includes winch
            includes_hitch_bar: Whether rental includes hitch bar
            furniture_blanket_count: Number of furniture blankets
            strap_chain_count: Number of straps/chains
            has_evening_pickup: Whether rental has evening pickup
            
        Returns:
            Dict with individual addon costs and total
        """
        if not settings:
            return {
                'winch_cost': Decimal('0'),
                'hitch_bar_cost': Decimal('0'),
                'furniture_blanket_cost': Decimal('0'),
                'strap_chain_cost': Decimal('0'),
                'evening_pickup_cost': Decimal('0'),
                'total_addon_cost': Decimal('0')
            }
            
        winch_cost = settings.winch_price if includes_winch else Decimal('0')
        hitch_bar_cost = settings.hitch_bar_price if includes_hitch_bar else Decimal('0')
        furniture_blanket_cost = settings.furniture_blanket_price * furniture_blanket_count
        strap_chain_cost = settings.strap_chain_price * strap_chain_count
        evening_pickup_cost = settings.evening_pickup_price if has_evening_pickup else Decimal('0')
        
        total_addon_cost = (
            winch_cost + hitch_bar_cost + furniture_blanket_cost + 
            strap_chain_cost + evening_pickup_cost
        )
        
        return {
            'winch_cost': winch_cost,
            'hitch_bar_cost': hitch_bar_cost,
            'furniture_blanket_cost': furniture_blanket_cost,
            'strap_chain_cost': strap_chain_cost,
            'evening_pickup_cost': evening_pickup_cost,
            'total_addon_cost': total_addon_cost
        }
    
    @staticmethod
    def calculate_totals(
        base_rate: Decimal,
        addon_costs: Decimal,
        extra_mileage: Decimal,
        tax_rate: Decimal,
        down_payment: Decimal = Decimal('0')
    ) -> Dict[str, Decimal]:
        """
        Calculate subtotal, tax, total, and balance.
        
        Args:
            base_rate: Base rental rate
            addon_costs: Total addon costs
            extra_mileage: Extra mileage charges
            tax_rate: Tax rate as percentage (e.g., 8.25 for 8.25%)
            down_payment: Down payment amount
            
        Returns:
            Dict with all calculated totals
        """
        subtotal = base_rate + addon_costs + extra_mileage
        tax_amount = subtotal * (tax_rate / Decimal('100'))
        total_amount = subtotal + tax_amount
        balance_due = total_amount - down_payment
        
        return {
            'subtotal': subtotal,
            'tax_amount': tax_amount,
            'total_amount': total_amount,
            'balance_due': balance_due
        }
    
    @staticmethod
    def format_duration_display(duration_info: Dict[str, Any]) -> str:
        """
        Format duration for display - Single source of truth for all duration formatting.
        
        This method shows the billing duration (what customer pays for), not mathematical duration.
        It aligns with the actual rate calculation logic in calculate_base_rate().
        
        Args:
            duration_info: Result from calculate_duration_info() containing:
                - rate_category: 'half_day', 'daily', 'weekly', or 'extended'
                - full_days: Number of complete days
                - has_half_day: Whether remainder qualifies as half-day increment
                - days: Total duration in decimal days
        
        Returns:
            Formatted duration string following billing logic:
            - Half day: "Half Day"
            - Daily with half-day: "3½ days" 
            - Daily with remainder > half-day: "4 days" (charges full day for remainder)
            - Weekly: "1 week"
            - Extended: "10 days" (rounded up)
        """
        if not duration_info:
            return 'Invalid duration'
        
        rate_category = duration_info.get('rate_category')
        full_days = duration_info.get('full_days', 0)
        has_half_day = duration_info.get('has_half_day', False)
        days = duration_info.get('days', 0)
        remainder = duration_info.get('remainder', 0)
        
        if rate_category == 'half_day':
            return 'Half Day'
        
        if rate_category == 'weekly':
            return '1 week'
        
        if rate_category == 'daily':
            # Follow the same logic as calculate_base_rate for billing consistency
            if remainder <= 0:
                # No remainder, just show full days
                display_days = max(full_days, 1)  # Minimum 1 day for daily rate
                return f"{display_days} day{'s' if display_days != 1 else ''}"
            elif has_half_day:
                # Remainder qualifies as half-day increment
                return f"{full_days}½ days"
            else:
                # Remainder is more than half-day, so we charge (and display) another full day
                billed_days = full_days + 1
                return f"{billed_days} day{'s' if billed_days != 1 else ''}"
        
        if rate_category == 'extended':
            import math
            rounded_days = math.ceil(days)
            return f"{rounded_days} day{'s' if rounded_days != 1 else ''}"
        
        # Fallback for unknown categories
        return f"{int(days)} day{'s' if int(days) != 1 else ''}"
    
    @staticmethod
    def calculate_complete_quote(
        trailer,
        start_datetime: datetime,
        end_datetime: datetime,
        settings,
        custom_rate: Optional[Decimal] = None,
        extra_mileage: Decimal = Decimal('0'),
        down_payment: Decimal = Decimal('0'),
        **addon_kwargs
    ) -> Dict[str, Any]:
        """
        Calculate a complete rental quote with all components.
        
        This is the main method that combines all calculations.
        
        Returns:
            Complete quote dictionary with all calculated values
        """
        # Calculate duration
        duration_info = RentalCalculator.calculate_duration_info(start_datetime, end_datetime)
        
        # Calculate base rate
        base_rate = RentalCalculator.calculate_base_rate(
            trailer, 
            duration_info['days'], 
            custom_rate
        )
        
        # Calculate addon costs
        addon_costs = RentalCalculator.calculate_addon_costs(settings, **addon_kwargs)
        
        # Calculate totals
        tax_rate = settings.tax_rate if settings else Decimal('0')
        totals = RentalCalculator.calculate_totals(
            base_rate,
            addon_costs['total_addon_cost'],
            extra_mileage,
            tax_rate,
            down_payment
        )
        
        # Combine all results
        quote = {
            'duration_info': duration_info,
            'base_rate': base_rate,
            'addon_costs': addon_costs,
            'extra_mileage': extra_mileage,
            'down_payment': down_payment,
            **totals
        }
        
        return quote
    
    @staticmethod
    def get_pricing_rules_display() -> list:
        """
        Get formatted pricing rules for display in templates.
        
        Returns:
            List of pricing rule strings
        """
        return [
            f"Half Day ({RentalCalculator.HALF_DAY_HOURS} hours or less): Half day rate applies",
            f"1-{RentalCalculator.DAILY_RATE_MAX_DAYS}.5 Days: Daily rate × full days + half day rate for increments (e.g., 1.5, 2.5, 3.5, 4.5 days)",
            f"{RentalCalculator.DAILY_RATE_MAX_DAYS + 1}-{RentalCalculator.WEEKLY_RATE_MAX_DAYS} Days: Flat weekly rate",
            f"{RentalCalculator.WEEKLY_RATE_MAX_DAYS + 1}+ Days: Extended daily rate (weekly rate ÷ {RentalCalculator.WEEKLY_RATE_DIVISOR}) × number of days"
        ]
    
    @staticmethod
    def get_calculation_constants() -> Dict[str, Any]:
        """
        Get all calculation constants for frontend use.
        
        Returns:
            Dictionary of constants
        """
        return {
            'HALF_DAY_HOURS': RentalCalculator.HALF_DAY_HOURS,
            'HALF_DAY_THRESHOLD': float(RentalCalculator.HALF_DAY_THRESHOLD),
            'DAILY_RATE_MAX_DAYS': RentalCalculator.DAILY_RATE_MAX_DAYS,
            'WEEKLY_RATE_MAX_DAYS': RentalCalculator.WEEKLY_RATE_MAX_DAYS,
            'WEEKLY_RATE_DIVISOR': RentalCalculator.WEEKLY_RATE_DIVISOR
        } 