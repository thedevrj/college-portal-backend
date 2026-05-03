from django.shortcuts import redirect
from django.urls import reverse

class ForcePasswordChangeMiddleware:
    """
    Middleware to force a user to change their password on first login.
    Intercepts the request and redirects to the password change form if flagged.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_superuser:
            try:
                if getattr(request.user, 'portal_profile', None) and request.user.portal_profile.force_password_change:
                    # Paths the user is allowed to access while locked
                    allowed_paths = [
                        reverse('admin:password_change'),
                        reverse('admin:password_change_done'),
                        reverse('portal_logout'),
                        reverse('admin:logout'), # Allow Django admin logout button
                    ]
                    
                    # If the current path is not allowed, redirect them
                    if request.path not in allowed_paths and not request.path.startswith('/static/') and not request.path.startswith('/media/'):
                        return redirect('admin:password_change')
            except Exception:
                pass
                
        response = self.get_response(request)
        return response
