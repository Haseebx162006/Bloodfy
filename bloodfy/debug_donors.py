import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodfy_project.settings')
django.setup()

from users.models import User
from donors.models import Donor

print("--- USERS (Donor Type) ---")
for user in User.objects.filter(user_type='donor'):
    print(f"User: {user.email}, Status: {user.donor_status}, Type: {user.user_type}")

print("\n--- DONORS ---")
for donor in Donor.objects.all():
    print(f"Donor: {donor.user.email}, Blood: {donor.blood_group}, Active: {donor.is_active}, Eligible: {donor.is_eligible}")
    print(f"  -> User Status: {donor.user.donor_status}")
