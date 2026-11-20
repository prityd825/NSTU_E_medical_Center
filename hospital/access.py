"""Role-based access control for the E-Medical app.

Every logged-in page is protected with ``@role_required(...)`` (function views) or
``RoleRequiredMixin`` (class views). Rules:

* Not logged in            -> sent to the sign-in page of the first allowed role, then back.
* Logged in, wrong role    -> sent to *their own* dashboard with a short notice.
* Doctor/patient/accountant whose account is not approved yet -> "waiting for approval" page.
* Administrators are a role of their own; pass 'admin' explicitly where they may also enter.
"""
from functools import wraps

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect

from . import models

ADMIN, DOCTOR, PATIENT, ACCOUNTANT = 'admin', 'doctor', 'patient', 'accountant'

ROLE_HOME = {
    ADMIN: 'admin-dashboard',
    DOCTOR: 'doctor-dashboard',
    PATIENT: 'patient-dashboard',
    ACCOUNTANT: 'accountant-dashboard',
}
ROLE_LOGIN = {
    ADMIN: '/adminlogin',
    DOCTOR: '/doctorlogin',
    PATIENT: '/patientlogin',
    ACCOUNTANT: '/accountantlogin',
}
ROLE_LABEL = {ADMIN: 'administrators', DOCTOR: 'doctors', PATIENT: 'patients', ACCOUNTANT: 'accountants'}
PROFILE_MODEL = {DOCTOR: models.Doctor, PATIENT: models.Patient, ACCOUNTANT: models.Accountant}


def get_role(user):
    """Return 'admin' | 'doctor' | 'patient' | 'accountant' | None for a user."""
    if user is None or not user.is_authenticated:
        return None
    cached = getattr(user, '_em_role', False)
    if cached is not False:
        return cached
    groups = set(user.groups.values_list('name', flat=True))
    if 'ADMIN' in groups or user.is_superuser:
        role = ADMIN
    elif 'DOCTOR' in groups:
        role = DOCTOR
    elif 'PATIENT' in groups:
        role = PATIENT
    elif 'ACCOUNTANT' in groups:
        role = ACCOUNTANT
    else:
        role = None
    user._em_role = role
    return role


def get_profile(user):
    """The Doctor / Patient / Accountant row for this user (None for admins)."""
    model = PROFILE_MODEL.get(get_role(user))
    return model.objects.filter(user=user).first() if model else None


def is_approved(user):
    role = get_role(user)
    if role == ADMIN:
        return True
    if role is None:
        return False
    profile = get_profile(user)
    return bool(profile and profile.status)


def check_access(request, roles):
    """Return None when the request may continue, otherwise the redirect response to send."""
    user = request.user
    if not user.is_authenticated:
        return redirect_to_login(request.get_full_path(), ROLE_LOGIN.get(roles[0], '/'))
    role = get_role(user)
    if role is None:
        messages.error(request, 'Your account has no role yet. Please contact the medical center.')
        return redirect('/')
    if role not in roles:
        allowed = ' and '.join(ROLE_LABEL[r] for r in roles)
        messages.warning(request, f'That page is only for {allowed}. Here is your dashboard instead.')
        return redirect(ROLE_HOME[role])
    if not is_approved(user):
        return redirect('afterlogin')  # shows the "waiting for approval" page
    return None


def role_required(*roles):
    """Decorator: @role_required('doctor') or @role_required('doctor', 'admin')."""
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            denied = check_access(request, roles)
            if denied is not None:
                return denied
            return view(request, *args, **kwargs)
        return wrapper
    return decorator


class RoleRequiredMixin:
    """Class-based-view version: set ``allowed_roles = ('doctor',)``."""
    allowed_roles = ()

    def dispatch(self, request, *args, **kwargs):
        denied = check_access(request, self.allowed_roles)
        if denied is not None:
            return denied
        return super().dispatch(request, *args, **kwargs)


def post_required(view):
    """Approve / reject / delete must come from a button (POST), never from a plain link or a typed URL."""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if request.method != 'POST':
            messages.error(request, 'Please use the buttons on the page for that action.')
            return redirect(request.META.get('HTTP_REFERER') or 'afterlogin')
        return view(request, *args, **kwargs)
    return wrapper
