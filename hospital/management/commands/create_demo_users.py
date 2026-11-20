"""Create (or reset) one approved demo account for every role.

    python manage.py create_demo_users

Safe to run many times: existing demo users get their password and approval reset.
The logins are listed in README.md so anyone can try the app.
"""
import datetime

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand

from hospital import models

DEMO_PASSWORD = 'Demo@1234'

DEMO_USERS = [
    # username,        group,        first,    last,       email
    ('demo_admin',      'ADMIN',      'Demo',   'Admin',    'admin@demo.nstu'),
    ('demo_doctor',     'DOCTOR',     'Ayesha', 'Rahman',   'doctor@demo.nstu'),
    ('demo_patient',    'PATIENT',    'Tanvir', 'Hasan',    'patient@demo.nstu'),
    ('demo_accountant', 'ACCOUNTANT', 'Sadia',  'Islam',    'accountant@demo.nstu'),
]


class Command(BaseCommand):
    help = 'Create or reset the demo accounts (one per role) used in the README.'

    def handle(self, *args, **options):
        for username, group, first, last, email in DEMO_USERS:
            user, created = User.objects.get_or_create(username=username)
            user.first_name, user.last_name, user.email = first, last, email
            user.set_password(DEMO_PASSWORD)
            user.save()
            Group.objects.get_or_create(name=group)[0].user_set.add(user)

            if group == 'DOCTOR':
                models.Doctor.objects.update_or_create(user=user, defaults={
                    'address': 'NSTU Medical Center', 'email': email, 'department': 'Cardiologist', 'status': True})
            elif group == 'PATIENT':
                models.Patient.objects.update_or_create(user=user, defaults={
                    'address': 'Bangabandhu Hall, NSTU', 'email': email, 'status': True})
            elif group == 'ACCOUNTANT':
                models.Accountant.objects.update_or_create(user=user, defaults={
                    'address': 'Medical store, NSTU', 'email': email, 'status': True})

            self.stdout.write(f"{'created' if created else 'reset  '} {username}")

        # A little stock so the prescription form has something to pick on a fresh database.
        if not models.Medicine.objects.exists():
            today = datetime.date.today()
            for name, company, stock in [('Napa 500mg', 'Beximco', 500), ('Seclo 20mg', 'Square', 300),
                                         ('Fexo 120mg', 'Square', 200), ('Oral Saline', 'SMC', 400)]:
                models.Medicine.objects.create(date=today, medicinename=name, companyname=company, stock=stock)
            self.stdout.write('added starter medicines')

        self.stdout.write(self.style.SUCCESS(f'Demo accounts ready. Password for all: {DEMO_PASSWORD}'))
