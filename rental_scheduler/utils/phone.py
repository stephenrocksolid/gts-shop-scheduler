"""
Phone number formatting utilities.
"""
import re


def format_phone(value: str) -> str:
    """
    Format a phone number string to xxx-xxx-xxxx or 1-xxx-xxx-xxxx format.
    
    Accepts various input formats and normalizes them:
    - 5551234567 -> 555-123-4567
    - (555) 123-4567 -> 555-123-4567
    - 555-123-4567 -> 555-123-4567
    - 15551234567 -> 1-555-123-4567
    - 1 (555) 123-4567 -> 1-555-123-4567
    - Partial inputs are formatted as much as possible
    
    Args:
        value: The phone number string to format
        
    Returns:
        Formatted phone number string, or empty string if input is empty/None
    """
    if not value:
        return ''
    
    # Extract only digits
    digits = re.sub(r'\D', '', value)
    
    if not digits:
        return ''
    
    # Handle numbers starting with 1 (country code) - treat as 11 digit format
    if len(digits) >= 11 and digits[0] == '1':
        # Truncate to 11 digits and format as 1-xxx-xxx-xxxx
        digits = digits[:11]
        return f"1-{digits[1:4]}-{digits[4:7]}-{digits[7:11]}"
    
    # Truncate to 10 digits if more
    if len(digits) > 10:
        digits = digits[:10]
    
    # Format based on length
    if len(digits) <= 3:
        return digits
    elif len(digits) <= 6:
        return f"{digits[:3]}-{digits[3:]}"
    else:
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"

