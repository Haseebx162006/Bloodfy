"""
Django management command to create an admin user interactively.

Usage:
    python manage.py create_admin

Or with arguments (non-interactive):
    python manage.py create_admin --email admin@example.com --password Admin@1234 --first_name John --last_name Doe
"""

import getpass
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError


class Command(BaseCommand):
    help = 'Create an admin user and save it to the database'

    def add_arguments(self, parser):
        parser.add_argument('--email',      type=str, help='Admin email address')
        parser.add_argument('--password',   type=str, help='Admin password (min 8 chars, include uppercase, number, symbol)')
        parser.add_argument('--first_name', type=str, help='First name', default='')
        parser.add_argument('--last_name',  type=str, help='Last name',  default='')

    def handle(self, *args, **options):
        from users.models import User

        self.stdout.write(self.style.MIGRATE_HEADING('\n=== Bloodify Admin Creator ===\n'))

        # ── gather email ──────────────────────────────────────────────────────
        email = options.get('email')
        if not email:
            email = input('  Email address: ').strip()
        if not email:
            raise CommandError('Email is required.')

        if User.objects.filter(email__iexact=email).exists():
            raise CommandError(f'A user with email "{email}" already exists.')

        # ── gather password ───────────────────────────────────────────────────
        password = options.get('password')
        if not password:
            password = getpass.getpass('  Password: ')
            confirm  = getpass.getpass('  Confirm password: ')
            if password != confirm:
                raise CommandError('Passwords do not match.')

        if len(password) < 8:
            raise CommandError('Password must be at least 8 characters long.')

        # ── gather name ───────────────────────────────────────────────────────
        first_name = options.get('first_name') or input('  First name (optional): ').strip()
        last_name  = options.get('last_name')  or input('  Last name  (optional): ').strip()

        # ── create user ───────────────────────────────────────────────────────
        try:
            user = User.objects.create_superuser(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
        except IntegrityError as e:
            raise CommandError(f'Database error: {e}')

        self.stdout.write(self.style.SUCCESS(
            f'\n✅  Admin created successfully!'
            f'\n    ID         : {user.id}'
            f'\n    Email      : {user.email}'
            f'\n    Name       : {user.get_full_name() or "(not set)"}'
            f'\n    user_type  : {user.user_type}'
            f'\n    is_staff   : {user.is_staff}'
            f'\n    is_superuser: {user.is_superuser}'
            f'\n    is_active  : {user.is_active}'
            f'\n    is_verified: {user.is_verified}'
            f'\n\nYou can now log in at the admin panel with these credentials.\n'
        ))
