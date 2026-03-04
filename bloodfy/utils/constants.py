"""
Constants for Bloodfy application.
"""

# Blood Group Choices
BLOOD_GROUPS = [
    ('A+', 'A Positive'),
    ('A-', 'A Negative'),
    ('B+', 'B Positive'),
    ('B-', 'B Negative'),
    ('O+', 'O Positive'),
    ('O-', 'O Negative'),
    ('AB+', 'AB Positive'),
    ('AB-', 'AB Negative'),
]

BLOOD_GROUP_VALUES = [bg[0] for bg in BLOOD_GROUPS]

# Blood Compatibility Matrix (recipient can receive from)
BLOOD_COMPATIBILITY = {
    'A+': ['A+', 'A-', 'O+', 'O-'],
    'A-': ['A-', 'O-'],
    'B+': ['B+', 'B-', 'O+', 'O-'],
    'B-': ['B-', 'O-'],
    'O+': ['O+', 'O-'],
    'O-': ['O-'],
    'AB+': ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-'],
    'AB-': ['A-', 'B-', 'O-', 'AB-'],
}

# User Types (FIXED - DO NOT CHANGE)
USER_TYPES = [
    ('user', 'User'),
    ('admin', 'Administrator'),
]

# Donor Status (for users who want to become donors)
DONOR_STATUS = [
    ('DONOR_PENDING', 'Pending Approval'),
    ('DONOR_APPROVED', 'Approved'),
    ('DONOR_REJECTED', 'Rejected'),
]

DONOR_STATUS_VALUES = [status[0] for status in DONOR_STATUS]

# Urgency Levels for Blood Requests
URGENCY_LEVELS = [
    ('normal', 'Normal'),
    ('urgent', 'Urgent'),
    ('emergency', 'Emergency'),
]

# Blood Request Status
REQUEST_STATUS = [
    ('pending', 'Pending'),
    ('matched', 'Matched'),
    ('assigned', 'Assigned'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
]

# Notification Types
NOTIFICATION_TYPES = [
    ('sms', 'SMS'),
    ('email', 'Email'),
    ('push', 'Push Notification'),
]

# Delivery Status
DELIVERY_STATUS = [
    ('pending', 'Pending'),
    ('sent', 'Sent'),
    ('failed', 'Failed'),
    ('delivered', 'Delivered'),
]

# Response Status (donor response to notification)
RESPONSE_STATUS = [
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('declined', 'Declined'),
    ('no_response', 'No Response'),
]

# Donation Status
DONATION_STATUS = [
    ('scheduled', 'Scheduled'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
]

# Eligibility Constants
DONATION_ELIGIBILITY_DAYS = 90  # Days required between donations

# AI Ranking Weights
AI_RANKING_WEIGHTS = {
    'compatibility': 0.40,  # 40%
    'distance': 0.30,       # 30%
    'responsiveness': 0.20, # 20%
    'eligibility': 0.10,    # 10%
}

# Distance Constants (in kilometers)
MAX_SEARCH_RADIUS_KM = 50  # Maximum search radius for donors
DISTANCE_SCORE_RANGES = [
    (5, 100),    # 0-5 km = 100 points
    (10, 80),    # 5-10 km = 80 points
    (20, 60),    # 10-20 km = 60 points
    (30, 40),    # 20-30 km = 40 points
    (50, 20),    # 30-50 km = 20 points
]

# Pagination
DEFAULT_PAGE_SIZE = 25
MAX_PAGE_SIZE = 100

# Pakistani Phone Number Format
PAKISTAN_PHONE_REGEX = r'^(\+92|0)?3[0-9]{9}$'

# CNIC Format (Pakistani National ID)
CNIC_REGEX = r'^\d{5}-\d{7}-\d{1}$'

# Cities in Pakistan (for validation/filtering)
PAKISTAN_CITIES = [
    'Karachi', 'Lahore', 'Islamabad', 'Rawalpindi', 'Faisalabad',
    'Multan', 'Peshawar', 'Quetta', 'Sialkot', 'Gujranwala',
    'Hyderabad', 'Bahawalpur', 'Sargodha', 'Sukkur', 'Larkana',
    'Sheikhupura', 'Jhang', 'Rahim Yar Khan', 'Gujrat', 'Mardan',
]
