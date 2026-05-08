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
