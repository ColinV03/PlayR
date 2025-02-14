from django import template

register = template.Library()

@register.filter
def format_decimal_minutes(decimal_minutes):
    """
    Formats decimal minutes (e.g., 12.5) into a minutes:seconds string (e.g., 12:30).
    """
    try:
        decimal_minutes = float(decimal_minutes)  # Handle float input directly
        if decimal_minutes < 0:
            return "0:00"  # Or handle negative values appropriately
        
        if decimal_minutes == 0:
            return "No Time Specified"

        minutes = int(decimal_minutes)
        seconds = int(round((decimal_minutes - minutes) * 60))  # Round seconds

        return f"{minutes}:{seconds:02d} minutes"  # Format seconds to two digits
    except (ValueError, TypeError):
        return ""  # Or handle invalid input as needed