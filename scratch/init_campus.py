import os
import sys
import django

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "college_backend_portal.settings")
django.setup()

from apps.academics.models import Department


def run():
    updated = Department.objects.filter(campus__isnull=True).update(campus="BBAU")
    print(f"Updated {updated} departments to campus: BBAU")
    # Also update any that were 'default' but might need explicit tagging
    all_depts = Department.objects.all().update(campus="BBAU")
    print("All existing departments have been initialized to BBAU.")


if __name__ == "__main__":
    run()
