from . import models
from .access import get_role, get_profile


def em_nav(request):
    """Expose the logged-in user's role, profile and (for admins) pending counts to every template."""
    user = getattr(request, 'user', None)
    if user is None or not user.is_authenticated:
        return {}

    role = get_role(user)
    ctx = {'nav_role': role, 'nav_profile': get_profile(user), 'nav_pending': {}}
    if role == 'admin':
        ctx['nav_pending'] = {
            'doctors': models.Doctor.objects.filter(status=False).count(),
            'patients': models.Patient.objects.filter(status=False).count(),
            'accountants': models.Accountant.objects.filter(status=False).count(),
            'appointments': models.Appointment.objects.filter(status=False).count(),
        }
    return ctx
