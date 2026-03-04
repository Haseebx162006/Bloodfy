# Generated migration file - Data migration for existing users

from django.db import migrations


def migrate_existing_users(apps, schema_editor):
    """
    Migrate existing users from old user_type system to new donor_status system.
    - Users with user_type='donor' → user_type='user' + donor_status='DONOR_APPROVED'
    - Users with user_type='recipient' → user_type='user'
    - Users with existing Donor profiles get donor_status='DONOR_APPROVED'
    """
    User = apps.get_model('users', 'User')
    Donor = apps.get_model('donors', 'Donor')
    
    # Get all users with donor profiles
    donor_user_ids = set(Donor.objects.values_list('user_id', flat=True))
    
    # Update users with donor_type='donor' or who have donor profiles
    for user in User.objects.all():
        updated = False
        
        # If user has a donor profile, they should be DONOR_APPROVED
        if user.id in donor_user_ids:
            user.donor_status = 'DONOR_APPROVED'
            updated = True
        
        # Change old user_type values to 'user'
        if user.user_type in ['donor', 'recipient']:
            user.user_type = 'user'
            updated = True
        
        if updated:
            user.save(update_fields=['user_type', 'donor_status'])


def reverse_migration(apps, schema_editor):
    """Reverse the migration (best effort)."""
    User = apps.get_model('users', 'User')
    Donor = apps.get_model('donors', 'Donor')
    
    donor_user_ids = set(Donor.objects.values_list('user_id', flat=True))
    
    for user in User.objects.all():
        if user.id in donor_user_ids:
            user.user_type = 'donor'
        else:
            user.user_type = 'recipient'
        user.donor_status = None
        user.save(update_fields=['user_type', 'donor_status'])


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_donor_status_user_donor_status_updated_at_and_more'),
        ('donors', '0003_donorrequest'),
    ]

    operations = [
        migrations.RunPython(migrate_existing_users, reverse_migration),
    ]
