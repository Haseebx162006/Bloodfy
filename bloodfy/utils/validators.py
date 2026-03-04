"""
Custom validators for Bloodfy application.
"""

import re
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.utils import timezone
from .constants import BLOOD_GROUP_VALUES, PAKISTAN_PHONE_REGEX, CNIC_REGEX, DONATION_ELIGIBILITY_DAYS


def validate_blood_group(value):
    """Validate that the blood group is one of the allowed values."""
    if value not in BLOOD_GROUP_VALUES:
        raise ValidationError(
            f"'{value}' is not a valid blood group. "
            f"Allowed values are: {', '.join(BLOOD_GROUP_VALUES)}"
        )


def validate_phone_number(value):
    """Validate Pakistani phone number format."""
    if not value:
        return
    
    # Remove any spaces or dashes
    cleaned = re.sub(r'[\s-]', '', value)
    
    if not re.match(PAKISTAN_PHONE_REGEX, cleaned):
        raise ValidationError(
            "Invalid phone number format. "
            "Use format: 03XXXXXXXXX or +923XXXXXXXXX"
        )


def validate_cnic(value):
    """Validate Pakistani CNIC format (XXXXX-XXXXXXX-X)."""
    if not value:
        return
    
    if not re.match(CNIC_REGEX, value):
        raise ValidationError(
            "Invalid CNIC format. Use format: XXXXX-XXXXXXX-X"
        )


def validate_latitude(value):
    """Validate latitude is within valid range."""
    if value is not None:
        if value < -90 or value > 90:
            raise ValidationError(
                "Latitude must be between -90 and 90 degrees."
            )


def validate_longitude(value):
    """Validate longitude is within valid range."""
    if value is not None:
        if value < -180 or value > 180:
            raise ValidationError(
                "Longitude must be between -180 and 180 degrees."
            )


def validate_units(value):
    """Validate blood units quantity."""
    if value < 1:
        raise ValidationError("Units must be at least 1.")
    if value > 100:
        raise ValidationError("Units cannot exceed 100.")


def validate_not_future_date(value):
    """Validate that a date is not in the future."""
    if value and value > date.today():
        raise ValidationError("Date cannot be in the future.")


def validate_donation_eligibility(last_donation_date):
    """
    Check if donor is eligible based on the 90-day rule.
    Returns (is_eligible, days_remaining, next_eligible_date)
    """
    if not last_donation_date:
        return True, 0, None
    
    today = date.today()
    next_eligible_date = last_donation_date + timedelta(days=DONATION_ELIGIBILITY_DAYS)
    
    if today >= next_eligible_date:
        return True, 0, next_eligible_date
    else:
        days_remaining = (next_eligible_date - today).days
        return False, days_remaining, next_eligible_date


def validate_password_strength(password):
    """Validate password meets strength requirements."""
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter.")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter.")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit.")
    
    if errors:
        raise ValidationError(errors)


def normalize_phone_number(phone):
    """Normalize phone number to standard format (+92XXXXXXXXXX)."""
    if not phone:
        return None
    
    # Remove spaces, dashes, and parentheses
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Convert to +92 format
    if cleaned.startswith('0'):
        cleaned = '+92' + cleaned[1:]
    elif cleaned.startswith('92'):
        cleaned = '+' + cleaned
    elif not cleaned.startswith('+92'):
        cleaned = '+92' + cleaned
    
    return cleaned
