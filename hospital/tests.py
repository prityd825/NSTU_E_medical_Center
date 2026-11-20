"""Role-based access and end-to-end flow tests.

Run:  python manage.py test hospital
Uses a fresh test database; the real db.sqlite3 is never touched.
"""
import datetime

from django.contrib.auth.models import Group, User
from django.test import TestCase

from . import models


def make_user(username, group, first='Test', last='User', email=None, password='pass12345!'):
    user = User.objects.create_user(username=username, password=password, first_name=first, last_name=last,
                                    email=email or f'{username}@example.com')
    Group.objects.get_or_create(name=group)[0].user_set.add(user)
    return user


class Base(TestCase):
    def setUp(self):
        self.admin = make_user('admin', 'ADMIN', 'Ada', 'Admin')
        self.doc_user = make_user('doc', 'DOCTOR', 'Dora', 'Doctor')
        self.doctor = models.Doctor.objects.create(user=self.doc_user, address='Campus', email=self.doc_user.email,
                                                   department='Cardiologist', status=True)
        self.doc2_user = make_user('doc2', 'DOCTOR', 'Dan', 'Second')
        self.doctor2 = models.Doctor.objects.create(user=self.doc2_user, address='Campus', email=self.doc2_user.email, status=True)
        self.pat_user = make_user('pat', 'PATIENT', 'Pia', 'Patient')
        self.patient = models.Patient.objects.create(user=self.pat_user, address='Hall 1', email=self.pat_user.email, status=True)
        self.pat2_user = make_user('pat2', 'PATIENT', 'Paul', 'Other')
        self.patient2 = models.Patient.objects.create(user=self.pat2_user, address='Hall 2', email=self.pat2_user.email, status=True)
        self.acc_user = make_user('acc', 'ACCOUNTANT', 'Ali', 'Accountant')
        self.accountant = models.Accountant.objects.create(user=self.acc_user, address='Office', email=self.acc_user.email, status=True)
        self.medicine = models.Medicine.objects.create(date=datetime.date(2024, 1, 1), medicinename='Paracetamol',
                                                       companyname='Square', stock=50)

    def as_(self, user):
        self.client.force_login(user)
        return self.client


ADMIN_URLS = ['/admin-dashboard', '/admin-doctor', '/admin-view-doctor', '/admin-add-doctor', '/admin-approve-doctor',
              '/admin-view-doctor-specialisation', '/admin-patient', '/admin-view-patient', '/admin-add-patient',
              '/admin-approve-patient', '/admin-accountant', '/admin-view-accountant', '/admin-add-accountant',
              '/admin-approve-accountant', '/admin-appointment', '/admin-view-appointment', '/admin-add-appointment',
              '/admin-approve-appointment', '/admin-medicine', '/admin-feedback', '/admin-prescriptions', '/admin-blog']
DOCTOR_URLS = ['/doctor-dashboard', '/doctor-appointment', '/doctor-view-appointment', '/doctor-delete-appointment',
               '/prescribe/', '/prescription_history/', '/edit-profile-doctor/', '/new-blog/', '/doctor_messages/',
               '/search?query=a']
PATIENT_URLS = ['/patient-dashboard', '/patient-appointment', '/patient-book-appointment', '/patient-view-appointment',
                '/patient-view-doctor', '/patient-feedback', '/searchdoctor?query=a', '/edit-profile-patient/', '/select_doctor/']
ACCOUNTANT_URLS = ['/accountant-dashboard', '/accountant-medicine', '/accountant-view-medicine', '/accountant-add-medicine',
                   '/search-medicine-records?start_date=2020-01-01&end_date=2030-01-01']
HOME = {'admin': '/admin-dashboard', 'doctor': '/doctor-dashboard', 'patient': '/patient-dashboard',
        'accountant': '/accountant-dashboard'}


class RoleAccessTests(Base):
    def users(self):
        return {'admin': self.admin, 'doctor': self.doc_user, 'patient': self.pat_user, 'accountant': self.acc_user}

    def test_each_role_sees_only_its_own_area(self):
        areas = {'admin': ADMIN_URLS, 'doctor': DOCTOR_URLS, 'patient': PATIENT_URLS, 'accountant': ACCOUNTANT_URLS}
        for role, user in self.users().items():
            client = self.as_(user)
            for area, urls in areas.items():
                for url in urls:
                    r = client.get(url)
                    if area == role:
                        self.assertEqual(r.status_code, 200, f'{role} should open {url}')
                    else:
                        self.assertEqual(r.status_code, 302, f'{role} must not open {url}')
                        self.assertEqual(r['Location'], HOME[role], f'{role} on {url} should go to own dashboard')

    def test_anonymous_is_sent_to_the_right_login(self):
        self.client.logout()
        for url, login in [('/admin-dashboard', '/adminlogin'), ('/doctor-dashboard', '/doctorlogin'),
                           ('/patient-dashboard', '/patientlogin'), ('/accountant-dashboard', '/accountantlogin')]:
            r = self.client.get(url)
            self.assertEqual(r.status_code, 302)
            self.assertTrue(r['Location'].startswith(login + '?next='), r['Location'])

    def test_afterlogin_routes_by_role(self):
        for role, user in self.users().items():
            r = self.as_(user).get('/afterlogin')
            self.assertRedirects(r, HOME[role], fetch_redirect_response=False)

    def test_unapproved_users_cannot_open_dashboards(self):
        u = make_user('newdoc', 'DOCTOR')
        models.Doctor.objects.create(user=u, address='x', status=False)
        c = self.as_(u)
        r = c.get('/doctor-dashboard')
        self.assertRedirects(r, '/afterlogin', fetch_redirect_response=False)
        r = c.get('/afterlogin')
        self.assertTemplateUsed(r, 'hospital/doctor_wait_for_approval.html')

    def test_dashboard_counts(self):
        r = self.as_(self.admin).get('/admin-dashboard')
        self.assertEqual(r.context['patientcount'], 2)  # every approved patient
        models.Appointment.objects.create(doctorId=self.doc_user.id, patientId=self.pat_user.id, description='x', status=True)
        r = self.as_(self.doc_user).get('/doctor-dashboard')
        self.assertEqual(r.context['patientcount'], 1)  # only this doctor's patients

    def test_sidebar_matches_role(self):
        r = self.as_(self.pat_user).get('/patient-dashboard')
        self.assertContains(r, 'Book appointment')
        self.assertNotContains(r, 'href="/admin-dashboard"')
        self.assertNotContains(r, 'href="/prescribe"')
        r = self.as_(self.admin).get('/admin-dashboard')
        self.assertContains(r, 'href="/admin-prescriptions"')
        self.assertNotContains(r, 'href="/patient-book-appointment"')


class AdminActionTests(Base):
    def test_approve_requires_post(self):
        u = make_user('pending', 'PATIENT')
        p = models.Patient.objects.create(user=u, address='x', status=False)
        c = self.as_(self.admin)
        c.get(f'/approve-patient/{p.id}')
        p.refresh_from_db()
        self.assertFalse(p.status, 'a GET must not approve')
        c.post(f'/approve-patient/{p.id}')
        p.refresh_from_db()
        self.assertTrue(p.status)

    def test_reject_and_delete_remove_user(self):
        c = self.as_(self.admin)
        r = c.post(f'/delete-doctor-from-hospital/{self.doctor2.id}')
        self.assertRedirects(r, '/admin-view-doctor', fetch_redirect_response=False)
        self.assertFalse(User.objects.filter(username='doc2').exists())
        self.assertEqual(c.post('/delete-doctor-from-hospital/9999').status_code, 404)

    def test_add_doctor_shows_errors_and_creates_approved_doctor(self):
        c = self.as_(self.admin)
        r = c.post('/admin-add-doctor', {'first_name': 'New'})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'This field is required')
        r = c.post('/admin-add-doctor', {'first_name': 'New', 'last_name': 'Doc', 'username': 'newdoc', 'email': 'n@x.com',
                                         'password': 'pw12345!', 'address': 'Campus', 'department': 'Cardiologist'})
        self.assertRedirects(r, '/admin-view-doctor', fetch_redirect_response=False)
        d = models.Doctor.objects.get(user__username='newdoc')
        self.assertTrue(d.status)
        self.assertEqual(d.email, 'n@x.com')

    def test_edit_without_password_keeps_password(self):
        c = self.as_(self.admin)
        r = c.post(f'/update-patient/{self.patient.id}', {'first_name': 'Pia', 'last_name': 'Changed', 'username': 'pat',
                                                          'email': 'pat@example.com', 'password': '', 'address': 'Hall 9'})
        self.assertRedirects(r, '/admin-view-patient', fetch_redirect_response=False)
        self.pat_user.refresh_from_db()
        self.assertEqual(self.pat_user.last_name, 'Changed')
        self.assertTrue(self.pat_user.check_password('pass12345!'))

    def test_edit_page_is_prefilled(self):
        r = self.as_(self.admin).get(f'/update-patient/{self.patient.id}')
        self.assertContains(r, 'value="Hall 1"')
        self.assertNotContains(r, 'This field is required')

    def test_admin_signup_locked_once_an_admin_exists(self):
        self.client.logout()
        r = self.client.get('/adminsignup')
        self.assertRedirects(r, '/adminlogin', fetch_redirect_response=False)
        self.assertEqual(self.as_(self.admin).get('/adminsignup').status_code, 200)

    def test_admin_can_read_every_prescription(self):
        rx = models.Prescription.objects.create(doctor=self.doctor, patient=self.patient, symptoms='Fever', tests='')
        r = self.as_(self.admin).get(f'/generate_pdf/{rx.id}/')
        self.assertEqual(r['Content-Type'], 'application/pdf')
        self.assertContains(self.as_(self.admin).get('/admin-prescriptions'), 'Fever')


class SignupTests(Base):
    def test_self_signup_cannot_self_approve(self):
        self.client.logout()
        r = self.client.post('/patientsignup', {'first_name': 'Sam', 'last_name': 'S', 'username': 'sam', 'email': 's@x.com',
                                                'password': 'pw12345!', 'address': 'Hall', 'status': 'on'})
        self.assertEqual(r.status_code, 302)
        self.assertFalse(models.Patient.objects.get(user__username='sam').status)

    def test_signup_errors_are_shown(self):
        self.client.logout()
        r = self.client.post('/doctorsignup', {'username': ''})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'This field is required')

    def test_wait_pages_logout_buttons_post(self):
        for role in ['patient', 'doctor', 'accountant']:
            u = make_user(f'wait_{role}', role.upper())
            {'patient': models.Patient, 'doctor': models.Doctor, 'accountant': models.Accountant}[role].objects.create(
                user=u, address='x', status=False)
            r = self.as_(u).get('/afterlogin')
            html = r.content.decode()
            self.assertTrue('data-method="post"' in html or 'method="post"' in html, f'{role} wait page logout must POST')

    def test_logout_link_goes_home_for_every_role(self):
        for user in [self.admin, self.doc_user, self.pat_user, self.acc_user]:
            c = self.as_(user)
            r = c.get('/logout', follow=True)
            self.assertEqual(r.redirect_chain[-1][0], '/')
            self.assertTemplateUsed(r, 'hospital/index.html')
            self.assertContains(r, 'You have been signed out.')
            self.assertFalse(r.context['user'].is_authenticated)

    def test_logout_works_with_post(self):
        c = self.as_(self.pat_user)
        r = c.post('/logout')
        self.assertRedirects(r, '/', fetch_redirect_response=False)
        self.assertEqual(c.get('/patient-dashboard').status_code, 302)


class AppointmentFlowTests(Base):
    def test_book_approve_and_doctor_sees_it(self):
        c = self.as_(self.pat_user)
        r = c.post('/patient-book-appointment', {'doctorId': self.doc_user.id, 'description': 'Headache'})
        self.assertRedirects(r, '/patient-view-appointment', fetch_redirect_response=False)
        appt = models.Appointment.objects.get(description='Headache')
        self.assertFalse(appt.status)
        self.assertEqual(appt.patientId, self.pat_user.id)

        self.as_(self.admin).post(f'/approve-appointment/{appt.id}')
        appt.refresh_from_db()
        self.assertTrue(appt.status)

        r = self.as_(self.doc_user).get('/doctor-view-appointment')
        self.assertContains(r, 'Headache')
        r = self.as_(self.doc2_user).get('/doctor-view-appointment')
        self.assertNotContains(r, 'Headache')

    def test_doctor_cannot_delete_another_doctors_appointment(self):
        appt = models.Appointment.objects.create(doctorId=self.doc_user.id, patientId=self.pat_user.id,
                                                 description='x', status=True)
        self.as_(self.doc2_user).post(f'/delete-appointment/{appt.id}')
        self.assertTrue(models.Appointment.objects.filter(id=appt.id).exists())
        self.as_(self.doc_user).get(f'/delete-appointment/{appt.id}')
        self.assertTrue(models.Appointment.objects.filter(id=appt.id).exists(), 'GET must not delete')
        self.as_(self.doc_user).post(f'/delete-appointment/{appt.id}')
        self.assertFalse(models.Appointment.objects.filter(id=appt.id).exists())


class PrescriptionFlowTests(Base):
    def test_full_prescription_flow(self):
        c = self.as_(self.doc_user)
        r = c.post('/prescribe/', {'patient_email': 'nobody@x.com'})
        self.assertContains(r, 'No patient is registered')
        r = c.post('/prescribe/', {'patient_email': 'PAT@example.com'})
        rx = models.Prescription.objects.get(patient=self.patient)
        self.assertRedirects(r, f'/prescription_form/{rx.id}/', fetch_redirect_response=False)

        r = c.post(f'/prescription_form/{rx.id}/', {'symptoms': 'Fever', 'medicine1': self.medicine.id,
                                                   'medicine1Count': 100, 'extraMedicine': '', 'advice': '', 'tests': ''})
        self.assertContains(r, 'Only 50 Paracetamol left')
        self.medicine.refresh_from_db()
        self.assertEqual(self.medicine.stock, 50)

        r = c.post(f'/prescription_form/{rx.id}/', {'symptoms': 'Fever', 'medicine1': self.medicine.id,
                                                   'medicine1Count': 10, 'extraMedicine': '', 'advice': 'Rest', 'tests': ''})
        self.assertRedirects(r, '/prescription_history/', fetch_redirect_response=False)
        self.medicine.refresh_from_db()
        self.assertEqual(self.medicine.stock, 40)

        # a saved prescription cannot be submitted again (would deduct stock twice)
        r = c.post(f'/prescription_form/{rx.id}/', {'symptoms': 'Again', 'medicine1': self.medicine.id, 'medicine1Count': 5,
                                                   'extraMedicine': '', 'advice': '', 'tests': ''})
        self.assertRedirects(r, '/prescription_history/', fetch_redirect_response=False)
        self.medicine.refresh_from_db()
        self.assertEqual(self.medicine.stock, 40)

        # the same medicine in two rows is checked against the stock together, and typed text is kept on error
        rx2 = models.Prescription.objects.create(doctor=self.doctor, patient=self.patient, symptoms='', tests='')
        r = c.post(f'/prescription_form/{rx2.id}/', {'symptoms': 'Cough', 'medicine1': self.medicine.id, 'medicine1Count': 30,
                                                    'medicine2': self.medicine.id, 'medicine2Count': 30,
                                                    'extraMedicine': '', 'advice': 'Warm water', 'tests': ''})
        self.assertContains(r, 'Only 40 Paracetamol left')
        self.assertContains(r, '>Cough</textarea>')
        self.assertContains(r, '>Warm water</textarea>')
        self.medicine.refresh_from_db()
        self.assertEqual(self.medicine.stock, 40)

        # owner patient can download, another patient cannot, the other doctor cannot
        self.assertEqual(self.as_(self.pat_user).get(f'/generate_pdf_patient/{rx.id}/')['Content-Type'], 'application/pdf')
        self.assertRedirects(self.as_(self.pat2_user).get(f'/generate_pdf_patient/{rx.id}/'), '/patient-dashboard',
                             fetch_redirect_response=False)
        self.assertRedirects(self.as_(self.doc2_user).get(f'/generate_pdf/{rx.id}/'), '/prescription_history/',
                             fetch_redirect_response=False)
        self.assertRedirects(self.as_(self.doc2_user).get(f'/prescription_form/{rx.id}/'), '/prescription_history/',
                             fetch_redirect_response=False)


class ChatTests(Base):
    def test_patient_doctor_chat_is_private(self):
        c = self.as_(self.pat_user)
        r = c.post(f'/send_message/{self.doc_user.id}/', {'content': 'Hello doctor'})
        msg = models.Message.objects.get(content='Hello doctor')
        self.assertRedirects(r, f'/message_list/{msg.chat_id}/{self.doc_user.id}/', fetch_redirect_response=False)

        d = self.as_(self.doc_user)
        d.post(f'/message_list/{msg.chat_id}/{self.pat_user.id}/', {'content': 'Hello patient'})
        reply = models.Message.objects.get(content='Hello patient')
        self.assertEqual(reply.recipient, self.pat_user)
        self.assertEqual(reply.chat_id, msg.chat_id)

        # Another patient can neither read nor post in this chat.
        o = self.as_(self.pat2_user)
        r = o.get(f'/message_list/{msg.chat_id}/{self.doc_user.id}/')
        self.assertNotContains(r, 'Hello doctor')
        o.post(f'/message_list/{msg.chat_id}/{self.doc_user.id}/', {'content': 'intruder'})
        self.assertFalse(models.Message.objects.filter(content='intruder').exists())

        # Starting again with the same doctor reuses the conversation.
        r = self.as_(self.pat_user).post('/select_doctor/', {'doctor': self.doctor.id})
        self.assertRedirects(r, f'/message_list/{msg.chat_id}/{self.doc_user.id}/', fetch_redirect_response=False)

    def test_pending_doctors_are_not_offered_for_chat(self):
        u = make_user('pendingdoc', 'DOCTOR', 'Pending', 'Doc')
        models.Doctor.objects.create(user=u, address='x', status=False)
        r = self.as_(self.pat_user).get('/select_doctor/')
        self.assertNotContains(r, 'Dr. Pending Doc (')
        self.assertContains(r, 'Dr. Dora Doctor (')

    def test_patients_cannot_message_patients(self):
        self.as_(self.pat_user).post(f'/send_message/{self.pat2_user.id}/', {'content': 'hi'})
        self.assertFalse(models.Message.objects.filter(content='hi').exists())


class FeedbackMedicineBlogTests(Base):
    def test_feedback_is_linked_to_patient(self):
        self.as_(self.pat_user).post('/patient-feedback', {'patientName': 'Pia', 'email': 'pat@example.com', 'feedback': 'Great'})
        fb = models.PatientFeedback.objects.get(feedback='Great')
        self.assertEqual(fb.patient, self.patient)
        self.assertContains(self.as_(self.admin).get('/admin-feedback'), 'Great')

    def test_accountant_medicine_crud(self):
        c = self.as_(self.acc_user)
        c.post('/accountant-add-medicine', {'date': '2024-02-02', 'medicinename': 'Napa', 'companyname': 'Beximco', 'stock': 30})
        m = models.Medicine.objects.get(medicinename='Napa')
        c.post(f'/update-medicine/{m.id}', {'date': '2024-02-02', 'medicinename': 'Napa', 'companyname': 'Beximco', 'stock': 35})
        m.refresh_from_db()
        self.assertEqual(m.stock, 35)
        c.post(f'/delete-medicine-from-hospital/{m.id}')
        self.assertFalse(models.Medicine.objects.filter(id=m.id).exists())
        # a patient cannot edit medicine
        self.as_(self.pat_user).post(f'/update-medicine/{self.medicine.id}', {'date': '2024-01-01', 'medicinename': 'X',
                                                                              'companyname': 'X', 'stock': 1})
        self.medicine.refresh_from_db()
        self.assertEqual(self.medicine.medicinename, 'Paracetamol')

    def test_medicine_validation(self):
        c = self.as_(self.acc_user)
        r = c.post('/accountant-add-medicine', {'date': '2024-02-02', 'medicinename': 'Napa', 'companyname': 'B', 'stock': -5})
        self.assertContains(r, 'Stock cannot be negative')
        r = c.post('/accountant-add-medicine', {'date': '2024-02-02', 'medicinename': 'paracetamol', 'companyname': 'B', 'stock': 5})
        self.assertContains(r, 'already on record')
        self.assertEqual(models.Medicine.objects.count(), 1)

    def test_blog_permissions(self):
        self.as_(self.pat_user).post('/new-blog/', {'title': 'Spam', 'content': 'x'})
        self.assertFalse(models.Post.objects.filter(title='Spam').exists())
        self.as_(self.doc_user).post('/new-blog/', {'title': 'First aid', 'content': 'Stay calm'})
        post = models.Post.objects.get(title='First aid')
        self.assertEqual(post.doctor, self.doctor)
        self.as_(self.doc2_user).post(f'/post/{post.id}/update/', {'title': 'Hacked', 'content': 'x'})
        post.refresh_from_db()
        self.assertEqual(post.title, 'First aid')
        self.client.logout()
        self.assertContains(self.client.get('/blog/'), 'First aid')
        self.assertContains(self.client.get(f'/post/{post.id}/'), 'Stay calm')
        self.as_(self.admin).post(f'/post/{post.id}/delete/')
        self.assertFalse(models.Post.objects.filter(id=post.id).exists())

    def test_public_pages(self):
        self.client.logout()
        for url in ['/', '/aboutus', '/contactus', '/blog/', '/patientlogin', '/patientsignup', '/password_reset/']:
            self.assertEqual(self.client.get(url).status_code, 200, url)
