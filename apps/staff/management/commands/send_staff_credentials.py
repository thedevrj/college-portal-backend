import csv
import logging
import secrets
import string
import time
from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives, get_connection
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from apps.accounts.models import UserProfile
from apps.staff.models import Staff

logger = logging.getLogger(__name__)


def generate_secure_password(length=10) -> str:
    """
    Generates a cryptographically strong temporary password.
    Guarantees at least 1 uppercase, 1 lowercase, 1 digit, and 1 safe symbol.
    """
    length = max(length, 8)
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    symbols = "@#$!%*"

    # Guarantee at least one of each category
    password = [
        secrets.choice(uppercase),
        secrets.choice(lowercase),
        secrets.choice(digits),
        secrets.choice(symbols),
    ]

    all_chars = uppercase + lowercase + digits + symbols
    for _ in range(length - 4):
        password.append(secrets.choice(all_chars))

    secrets.SystemRandom().shuffle(password)
    return "".join(password)


class Command(BaseCommand):
    help = (
        "Staff Module Command: Generate random temporary passwords for Staff members, "
        "enforce password change on first login, and send credentials to BOTH "
        "institutional and alternate emails if available."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simulate the entire process without modifying accounts or sending emails.",
        )
        parser.add_argument(
            "--test-email",
            type=str,
            help="Send a single sample credentials email to this address to verify layout & SMTP.",
        )
        parser.add_argument(
            "--staff-no",
            type=int,
            help="Process only a specific staff member by staff number.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=50,
            help="Number of emails per SMTP connection session (default: 50).",
        )
        parser.add_argument(
            "--delay",
            type=float,
            default=0.5,
            help="Delay in seconds between sending emails to avoid SMTP rate-limiting (default: 0.5s).",
        )
        parser.add_argument(
            "--portal-url",
            type=str,
            default=None,
            help="Base portal login URL (defaults to settings.FRONTEND_PORTAL_URL or '/accounts/login/').",
        )
        parser.add_argument(
            "--export-csv",
            type=str,
            default="staff_credentials_audit.csv",
            help="Path to export the CSV audit log (default: staff_credentials_audit.csv).",
        )
        parser.add_argument(
            "--password-length",
            type=int,
            default=10,
            help="Length of generated temporary password (default: 10).",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)
        test_email = options.get("test_email")
        target_staff_no = options.get("staff_no")
        batch_size = options.get("batch_size") or 50
        delay = options.get("delay") or 0.5
        csv_file_path = options.get("export_csv") or "staff_credentials_audit.csv"
        # Guarantee staff audit log never overwrites or appends to faculty audit log
        if csv_file_path == "faculty_credentials_audit.csv":
            self.stdout.write(
                self.style.WARNING(
                    "⚠️ Notice: 'faculty_credentials_audit.csv' is reserved for Faculty. Using 'staff_credentials_audit.csv' to keep audit logs separate."
                )
            )
            csv_file_path = "staff_credentials_audit.csv"

        pwd_length = options.get("password_length") or 10

        portal_url = options.get("portal_url")
        if not portal_url:
           portal_url = "https://login.bbau.ac.in/"

        from_email = getattr(
            settings,
            "DEFAULT_FROM_EMAIL",
            "BBAU University <no-reply@bbau.ac.in>",
        )

        self.stdout.write(self.style.MIGRATE_HEADING("=" * 70))
        self.stdout.write(
            self.style.MIGRATE_HEADING("  STAFF MODULE: CREDENTIALS DISPATCH & FIRST-LOGIN SETUP")
        )
        self.stdout.write(self.style.MIGRATE_HEADING("=" * 70))
        self.stdout.write(f"Portal Login URL:    {portal_url}")
        self.stdout.write(f"Sender (From):       {from_email}")
        self.stdout.write(f"Delay Between Mails:  {delay}s")
        self.stdout.write(f"Audit CSV Output:    {csv_file_path}")
        self.stdout.write(f"Delivery Target:     BOTH emails (insti_email + other_email if present)")
        if dry_run:
            self.stdout.write(
                self.style.WARNING("MODE: [DRY-RUN] No database records or emails will be sent.\n")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("MODE: [LIVE] Passwords will be updated and emails dispatched.\n")
            )

        # --- TEST EMAIL MODE ---
        if test_email:
            self.stdout.write(f"Sending sample test email to: {test_email} ...")
            sample_password = generate_secure_password(pwd_length)
            context = {
                "staff_name": "Test Staff Member",
                "username": "staff_9999",
                "temp_password": sample_password,
                "login_url": portal_url,
            }
            try:
                html_body = render_to_string("emails/staff_credentials.html", context)
                text_body = render_to_string("emails/staff_credentials.txt", context)
                msg = EmailMultiAlternatives(
                    subject="[TEST] Login Credentials - BBAU University",
                    body=text_body,
                    from_email=from_email,
                    to=[test_email],
                )
                msg.attach_alternative(html_body, "text/html")
                msg.send(fail_silently=False)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Test email successfully sent to {test_email}!\n"
                        f"  Sample Username: staff_9999 | Sample Password: {sample_password}"
                    )
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ Failed to send test email: {e}"))
            return

        # --- QUERY STAFF ---
        queryset = Staff.objects.filter(is_active=True).select_related("user")
        if target_staff_no:
            queryset = queryset.filter(staff_no=target_staff_no)

        total_staff = queryset.count()
        if total_staff == 0:
            self.stdout.write(self.style.WARNING("No active staff found matching criteria."))
            return

        self.stdout.write(f"Found {total_staff} active staff member(s) to process.\n")

        audit_records = []
        sent_count = 0
        missing_email_count = 0
        error_count = 0
        dual_email_count = 0

        # Shared connection for performance & reducing SMTP handshake overhead
        connection = None
        if not dry_run:
            try:
                connection = get_connection()
                connection.open()
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Could not open SMTP connection: {e}")
                )
                self.stdout.write("Aborting dispatch to protect against mass failures.")
                return

        try:
            for index, staff in enumerate(queryset, start=1):
                staff_no = staff.staff_no
                if not staff_no:
                    self.stdout.write(
                        self.style.WARNING(
                            f"[{index}/{total_staff}] Skipped {staff.name} (No staff_no assigned)"
                        )
                    )
                    audit_records.append(
                        {
                            "staff_no": "",
                            "name": staff.name,
                            "emails": "",
                            "username": "",
                            "status": "SKIPPED_NO_STAFF_NO",
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                    continue

                username = f"staff_{staff_no}"

                # Collect BOTH emails if present
                recipients = []
                if staff.insti_email and staff.insti_email.strip():
                    recipients.append(staff.insti_email.strip())
                if staff.other_email and staff.other_email.strip():
                    other_clean = staff.other_email.strip()
                    # Avoid duplicate if both emails are identical
                    if other_clean.lower() not in [r.lower() for r in recipients]:
                        recipients.append(other_clean)

                if not recipients:
                    missing_email_count += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"[{index}/{total_staff}] ⚠️  {staff.name} (Staff No: {staff_no}) - No email on record. Skipped."
                        )
                    )
                    audit_records.append(
                        {
                            "staff_no": staff_no,
                            "name": staff.name,
                            "emails": "",
                            "username": username,
                            "status": "SKIPPED_NO_EMAIL",
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                    continue

                if len(recipients) > 1:
                    dual_email_count += 1

                recipient_str = ", ".join(recipients)
                temp_password = generate_secure_password(pwd_length)

                if dry_run:
                    self.stdout.write(
                        f"[{index}/{total_staff}] [SIMULATE] Would update {username} -> Mails: [{recipient_str}] -> Pass: {temp_password}"
                    )
                    sent_count += 1
                    audit_records.append(
                        {
                            "staff_no": staff_no,
                            "name": staff.name,
                            "emails": recipient_str,
                            "username": username,
                            "status": "DRY_RUN_OK",
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                    continue

                # --- LIVE EXECUTION: DATABASE UPDATE ---
                try:
                    user = staff.user
                    if not user:
                        user = User.objects.filter(username=username).first()
                        if user:
                            staff.user = user
                            staff.save(update_fields=["user"])

                    primary_email = recipients[0]
                    if not user:
                        user = User.objects.create_user(
                            username=username,
                            email=primary_email,
                            password=temp_password,
                            is_staff=True,
                        )
                        staff.user = user
                        staff.save(update_fields=["user"])
                    else:
                        user.set_password(temp_password)
                        user.email = primary_email
                        user.is_staff = True
                        user.save()

                    # Name sync
                    name_parts = staff.name.strip().split(" ")
                    user.first_name = name_parts[0][:150]
                    user.last_name = " ".join(name_parts[1:])[:150]
                    user.save(update_fields=["first_name", "last_name", "email", "is_staff"])

                    # UserProfile setup (Non-teaching staff: force password change on first login)
                    profile, _ = UserProfile.objects.get_or_create(user=user)
                    profile.force_password_change = True
                    profile.employee_id = str(staff_no)
                    profile.save()

                except Exception as db_err:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f"[{index}/{total_staff}] ✗ DB Error for {username} ({staff.name}): {db_err}"
                        )
                    )
                    audit_records.append(
                        {
                            "staff_no": staff_no,
                            "name": staff.name,
                            "emails": recipient_str,
                            "username": username,
                            "status": f"DB_ERROR: {str(db_err)}",
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                    continue

                # --- LIVE EXECUTION: DISPATCH EMAIL TO BOTH EMAILS ---
                context = {
                    "staff_name": staff.name,
                    "username": username,
                    "temp_password": temp_password,
                    "login_url": portal_url,
                }
                try:
                    html_body = render_to_string("emails/staff_credentials.html", context)
                    text_body = render_to_string("emails/staff_credentials.txt", context)

                    email_msg = EmailMultiAlternatives(
                        subject="Your Staff Portal Login Credentials - BBAU University",
                        body=text_body,
                        from_email=from_email,
                        to=recipients,  # Sends to BOTH emails
                        connection=connection,
                    )
                    email_msg.attach_alternative(html_body, "text/html")
                    email_msg.send(fail_silently=False)

                    sent_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"[{index}/{total_staff}] ✓ Sent to {staff.name} ({username} -> [{recipient_str}])"
                        )
                    )
                    audit_records.append(
                        {
                            "staff_no": staff_no,
                            "name": staff.name,
                            "emails": recipient_str,
                            "username": username,
                            "status": "SENT_SUCCESS",
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                except Exception as mail_err:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f"[{index}/{total_staff}] ✗ SMTP Error for {username} ([{recipient_str}]): {mail_err}"
                        )
                    )
                    audit_records.append(
                        {
                            "staff_no": staff_no,
                            "name": staff.name,
                            "emails": recipient_str,
                            "username": username,
                            "status": f"SMTP_ERROR: {str(mail_err)}",
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                    # Attempt connection refresh on SMTP error
                    try:
                        if connection:
                            connection.close()
                        connection = get_connection()
                        connection.open()
                    except Exception:
                        pass

                # Periodically refresh SMTP connection every batch_size emails
                if index % batch_size == 0 and connection:
                    try:
                        connection.close()
                        connection = get_connection()
                        connection.open()
                    except Exception:
                        pass

                # Throttle slightly between sends
                if delay > 0:
                    time.sleep(delay)

        finally:
            if connection:
                try:
                    connection.close()
                except Exception:
                    pass

        # --- WRITE AUDIT CSV ---
        try:
            with open(csv_file_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f, fieldnames=["staff_no", "name", "emails", "username", "status", "timestamp"]
                )
                writer.writeheader()
                writer.writerows(audit_records)
            self.stdout.write(
                self.style.SUCCESS(f"\nAudit record saved to: {csv_file_path}")
            )
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Failed to write CSV audit log: {e}"))

        # --- SUMMARY ---
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("              STAFF DISPATCH SUMMARY")
        self.stdout.write("=" * 50)
        self.stdout.write(f"Total Active Staff:      {total_staff}")
        self.stdout.write(
            self.style.SUCCESS(f"Successfully Dispatched: {sent_count}")
        )
        self.stdout.write(
            self.style.SUCCESS(f"Recipients with Both Mails: {dual_email_count}")
        )
        self.stdout.write(
            self.style.WARNING(f"Skipped (Missing Email): {missing_email_count}")
        )
        self.stdout.write(
            self.style.ERROR(f"Failed (Errors):         {error_count}")
        )
        self.stdout.write("=" * 50)
