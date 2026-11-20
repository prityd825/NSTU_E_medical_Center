from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def active(context, *prefixes):
    """Return 'active' when the current path starts with any of the given prefixes.

    Usage: <a class="sidebar-link {% active '/admin-doctor' '/update-doctor' %}" ...>
    """
    request = context.get('request')
    if request is None:
        return ''
    path = request.path.rstrip('/') or '/'
    for prefix in prefixes:
        p = prefix.rstrip('/') or '/'
        if path == p or (p != '/' and path.startswith(p + '/')):
            return 'active'
    return ''


@register.filter
def initials(name):
    """'Rahim Uddin' -> 'RU'."""
    parts = [p for p in str(name or '').split() if p]
    if not parts:
        return '?'
    return ''.join(p[0] for p in parts[:2]).upper()
