from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender="academics.Department")
def sync_hod_portal_access(sender, instance, created, **kwargs):
    """
    DEACTIVATED: This logic was causing duplicate accounts for multi-login setups.
    Portal access for HODs should now be managed manually in the Admin.
    """
    pass


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create a UserProfile whenever a new User is created."""
    from apps.accounts.models import UserProfile

    if created:
        UserProfile.objects.get_or_create(
            user=instance, defaults={"force_password_change": True}
        )


from django.db.models.signals import pre_save


@receiver(pre_save, sender=User)
def auto_unlock_password_change(sender, instance, **kwargs):
    """
    Detects if a user has changed their password.
    If so, and they were locked in 'force_password_change' mode, this unlocks them.
    """
    if not instance.pk:
        return

    try:
        old_user = User.objects.get(pk=instance.pk)
        # If the password hash in the database is different from the one being saved...
        if old_user.password != instance.password:
            profile = getattr(instance, "portal_profile", None)
            if profile and profile.force_password_change:
                profile.force_password_change = False
                profile.save(update_fields=["force_password_change"])
    except User.DoesNotExist:
        pass


from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    from apps.accounts.models import UserActivityLog
    ip_address = get_client_ip(request) if request else None
    user_agent = request.META.get('HTTP_USER_AGENT', '') if request else None
    UserActivityLog.objects.create(
        user=user,
        action=UserActivityLog.ActionType.LOGIN,
        ip_address=ip_address,
        user_agent=user_agent
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    from apps.accounts.models import UserActivityLog
    ip_address = get_client_ip(request) if request else None
    user_agent = request.META.get('HTTP_USER_AGENT', '') if request else None
    UserActivityLog.objects.create(
        user=user,
        action=UserActivityLog.ActionType.LOGOUT,
        ip_address=ip_address,
        user_agent=user_agent
    )

@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    from apps.accounts.models import UserActivityLog
    ip_address = get_client_ip(request) if request else None
    user_agent = request.META.get('HTTP_USER_AGENT', '') if request else None
    
    # Try to find the user by credentials
    user = None
    username = credentials.get('username')
    if username:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            pass

    UserActivityLog.objects.create(
        user=user,
        action=UserActivityLog.ActionType.LOGIN_FAILED,
        ip_address=ip_address,
        user_agent=user_agent
    )
