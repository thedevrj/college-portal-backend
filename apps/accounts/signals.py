from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender="academics.Department")
def sync_hod_portal_access(sender, instance, created, **kwargs):
    """
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
    Detects if a user has changed their password if yes change to false.
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


from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)


def get_client_ip(request):
    return request.META.get("HTTP_X_REAL_IP") or request.META.get("REMOTE_ADDR")


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    from apps.accounts.models import UserActivityLog

    ip_address = get_client_ip(request) if request else None
    user_agent = request.META.get("HTTP_USER_AGENT", "") if request else None
    UserActivityLog.objects.create(
        user=user,
        action=UserActivityLog.ActionType.LOGIN,
        ip_address=ip_address,
        user_agent=user_agent,
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    from apps.accounts.models import UserActivityLog

    ip_address = get_client_ip(request) if request else None
    user_agent = request.META.get("HTTP_USER_AGENT", "") if request else None
    UserActivityLog.objects.create(
        user=user,
        action=UserActivityLog.ActionType.LOGOUT,
        ip_address=ip_address,
        user_agent=user_agent,
    )


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    from apps.accounts.models import UserActivityLog

    ip_address = get_client_ip(request) if request else None
    user_agent = request.META.get("HTTP_USER_AGENT", "") if request else None

    # Try to find the user by credentials
    user = None
    username = credentials.get("username")
    if username:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            pass

    UserActivityLog.objects.create(
        user=user,
        action=UserActivityLog.ActionType.LOGIN_FAILED,
        ip_address=ip_address,
        user_agent=user_agent,
    )


@receiver(pre_save)
def sanitize_html_fields(sender, instance, **kwargs):

    # Globally sanitize all RichTextFields across the project to prevent XSS (Script Injection).

    # Exclude non-model instances or migration-related classes if any
    if not hasattr(instance, "_meta"):
        return

    # Avoid applying on 3rd party apps by restricting to our own apps
    if not instance._meta.app_label in [
        "academics",
        "accounts",
        "admission",
        "authorities",
        "centres",
        "faculty",
        "foundation_course",
        "mou",
        "notices",
        "research",
        "staff",
    ]:
        return

    try:
        import nh3
    except ImportError:
        return

    for field in instance._meta.fields:
        # Check if the field is a RichTextField (by its class name to avoid importing all apps)
        if field.__class__.__name__ == "RichTextField":
            value = getattr(instance, field.attname)
            if value and isinstance(value, str):
                # Clean the HTML value using nh3 which removes <script>, <iframe> etc
                clean_value = nh3.clean(value)
                setattr(instance, field.attname, clean_value)
