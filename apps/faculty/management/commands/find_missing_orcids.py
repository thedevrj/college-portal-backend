import urllib.request
import urllib.parse
import json
import time
from django.core.management.base import BaseCommand
from django.db.models import Q
from apps.faculty.models import Faculty

class Command(BaseCommand):
    help = "Find and assign missing ORCID IDs for faculty members by searching the ORCID public API."

    def add_arguments(self, parser):
        parser.add_argument(
            '--save',
            action='store_true',
            help='Save the found ORCID IDs to the database. Without this flag, it performs a dry run.',
        )

    def clean_name(self, full_name):
        # Remove common academic titles
        prefixes = ["Prof.", "Dr.", "Mr.", "Mrs.", "Ms.", "Er.", "Prof", "Dr"]
        parts = full_name.split()
        cleaned = [p for p in parts if p not in prefixes]
        
        if not cleaned:
            return "", ""
        
        if len(cleaned) == 1:
            return cleaned[0], ""
            
        # Return first name and last name
        return cleaned[0], cleaned[-1]

    def handle(self, *args, **options):
        save_mode = options['save']
        
        # Get active faculty with no ORCID ID
        faculty_list = Faculty.objects.filter(
            Q(orcid_id__isnull=True) | Q(orcid_id__exact=""), 
            is_deleted=False
        )
        
        total_faculty = faculty_list.count()
        if total_faculty == 0:
            self.stdout.write(self.style.SUCCESS("All faculty members already have an ORCID ID!"))
            return
            
        mode_str = "SAVE MODE" if save_mode else "DRY RUN MODE"
        self.stdout.write(self.style.WARNING(f"--- Starting ORCID Search ({mode_str}) ---"))
        self.stdout.write(f"Searching for {total_faculty} faculty members...\n")
        
        found_count = 0
        
        for faculty in faculty_list:
            first_name, last_name = self.clean_name(faculty.name)
            
            if not first_name or not last_name:
                self.stdout.write(self.style.ERROR(f"Skipping {faculty.name} - Could not parse first/last name."))
                continue
                
            # Query ORCID API
            # We strictly search for both names AND the specific university affiliation
            query = f'given-names:{first_name} AND family-name:{last_name} AND affiliation-org-name:"Babasaheb Bhimrao Ambedkar University"'
            encoded_query = urllib.parse.quote(query)
            
            url = f"https://pub.orcid.org/v3.0/search/?q={encoded_query}"
            headers = {"Accept": "application/json"}
            
            req = urllib.request.Request(url, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    if response.status == 200:
                        data = json.loads(response.read().decode("utf-8"))
                        results = data.get("result") or []
                        
                        if len(results) == 1:
                            # Exactly one match found!
                            orcid = results[0].get("orcid-identifier", {}).get("path")
                            dept_name = faculty.department.name if faculty.department else "No Dept"
                            
                            self.stdout.write(
                                self.style.SUCCESS(f"[MATCH] {faculty.name} ({dept_name}) -> {orcid}")
                            )
                            self.stdout.write(f"        Verify: https://orcid.org/{orcid}")
                            
                            if save_mode:
                                faculty.orcid_id = orcid
                                faculty.save(update_fields=['orcid_id'])
                            
                            found_count += 1
                            
                        elif len(results) > 1:
                            self.stdout.write(self.style.WARNING(f"[SKIP] {faculty.name} -> Found multiple matches ({len(results)}). Skipping to be safe."))
                        else:
                            # 0 results
                            pass
                            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error fetching for {faculty.name}: {str(e)}"))
                
            # Sleep briefly to respect API rate limits
            time.sleep(0.5)
            
        self.stdout.write("\n" + "-"*40)
        self.stdout.write(self.style.SUCCESS(f"Finished! Found highly confident matches for {found_count} out of {total_faculty} faculty members."))
        
        if not save_mode and found_count > 0:
            self.stdout.write(self.style.WARNING("NOTE: This was a Dry Run. No database changes were made."))
            self.stdout.write("To save these IDs to the database, run: python manage.py find_missing_orcids --save")
