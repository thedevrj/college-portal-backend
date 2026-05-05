def dashboard_stats(request):
    """
    Injects department statistics into the template context.
    Only active for authenticated portal users on the admin index page.
    """
    if not request.user.is_authenticated:
        return {}

    # Check if this is an admin/portal page
    if request.path.startswith('/admin/') or request.path.startswith('/portal/'):
        try:
            profile = request.user.portal_profile
            if profile.is_portal_user:
                return {
                    'portal_stats': profile.get_dashboard_stats(),
                    'user_name': request.user.first_name or request.user.username,
                    'user_avatar': profile.profile_photo.url if profile.profile_photo else None
                }
        except:
            pass

    return {}
