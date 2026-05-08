from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.faculty.models import Faculty
from apps.staff.models import Staff
from apps.accounts.models import UserProfile

class Command(BaseCommand):
    help = 'Retroactively create login accounts and UserProfiles for all existing Faculty and Staff'

    def handle(self, *args, **options):
        self.stdout.write("Starting account synchronization...")
        
        # Sync Faculty
        faculty_members = Faculty.objects.all()
        f_count = 0
        for f in faculty_members:
            # Trigger the save() method logic we just added
            f.save()
            f_count += 1
        
        self.stdout.write(self.style.SUCCESS(f"Successfully processed {f_count} Faculty members."))

        # Sync Staff
        staff_members = Staff.objects.all()
        s_count = 0
        for s in staff_members:
            # Trigger the save() method logic
            s.save()
            s_count += 1
            
        self.stdout.write(self.style.SUCCESS(f"Successfully processed {s_count} Staff members."))
        self.stdout.write(self.style.SUCCESS("Synchronization complete! All users now have login accounts and security flags."))
