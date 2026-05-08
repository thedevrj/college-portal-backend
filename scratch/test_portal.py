import os
import django

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_backend_portal.settings')
django.setup()

from django.contrib.auth.models import User
from apps.accounts.models import UserProfile, PortalAccess, EntityType
from apps.accounts.services import PortalStatsService

def run_diagnostic():
    print("--- STARTING PORTAL DIAGNOSTIC ---")
    
    # 1. Check User
    user = User.objects.filter(username='rd_cell_admin').first()
    if not user:
        print("ERROR: User 'cs_hod' not found!")
        return
    print(f"User: {user.username} (Staff: {user.is_staff})")
    
    # 2. Check Profile
    profile = getattr(user, 'portal_profile', None)
    if not profile:
        print("ERROR: No UserProfile linked to this user!")
    else:
        print(f"Is Portal User: {profile.is_portal_user}")
    
    # 3. Check Access Entry
    access = user.access_entries.filter(is_active=True).first()
    if not access:
        print("ERROR: No active PortalAccess entry found for this user!")
    else:
        print(f"Role: {access.role}")
        print(f"Entity Type: {access.entity_type}")
        print(f"Entity Name: {access.entity.name if access.entity else 'None'}")
        
        # 4. Test Stats Calculation directly
        print("\n--- TESTING STATS LOGIC ---")
        try:
            stats = PortalStatsService.get_user_stats(profile)
            print(f"Calculated Stats: {stats}")
            if not stats:
                print("WARNING: Stats returned an empty dictionary!")
        except Exception as e:
            print(f"CRITICAL ERROR in Stats Service: {e}")

    print("--- DIAGNOSTIC COMPLETE ---")

if __name__ == "__main__":
    run_diagnostic()
