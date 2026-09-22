import getpass
import re
from datetime import date
from html.parser import HTMLParser
from http.cookiejar import CookieJar
from pathlib import Path
from urllib.parse import quote, urlencode, urljoin
from urllib.request import HTTPCookieProcessor, Request, build_opener

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.notices.models import GlobalNotice

LOGIN_URL = "https://www.bbau.ac.in/NoticeLogin.aspx"
MAX_FILE_SIZE = 20 * 1024 * 1024


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.hidden = {}; self.inputs = []; self.form = None; self.links = []; self.current = None; self.in_anchor = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "form" and self.form is None: self.form = attrs
        elif tag == "input":
            if attrs.get("type", "").lower() == "hidden": self.hidden[attrs.get("name", "")] = attrs.get("value", "")
            elif attrs.get("name"): self.inputs.append(attrs)
        elif tag == "a":
            self.current = {"text": "", "date_text": "", "href": attrs.get("href", "")}
            self.in_anchor = True

    def handle_data(self, data):
        if self.current is not None:
            if self.in_anchor: self.current["text"] += data
            else: self.current["date_text"] += data

    def handle_endtag(self, tag):
        if tag == "a" and self.current is not None:
            self.in_anchor = False
        elif tag == "tr" and self.current is not None:
            self.links.append(self.current); self.current = None


def get_page(opener, url):
    with opener.open(Request(url, headers={"User-Agent": "BBAU private notice migration"}), timeout=30) as response:
        return response.geturl(), response.read().decode("utf-8", "ignore")


def notice_date(item, href):
    text = f"{item.get('date_text', '')} {href}"
    match = re.search(r"(\d{1,2})[./-](\d{1,2})[./-](\d{4})", text)
    if match:
        return date(int(match.group(3)), int(match.group(2)), int(match.group(1)))
    return date.today()


def notice_category(title):
    text = title.lower()
    if any(word in text for word in ("tender", "quotation", "procurement", "purchase")):
        return "Tenders"
    if any(word in text for word in ("interview", "appointment", "joining", "promotion", "retirement", "superannuation")):
        return "Appointment"
    if any(word in text for word in ("programme", "program", "seminar", "workshop", "meeting", "celebration", "lecture")):
        return "Event"
    return "Announcement"


class Command(BaseCommand):
    help = "Import authorized 2026 faculty/private notices from BBAU"

    def add_arguments(self, parser):
        parser.add_argument("--staff-no", required=True)
        parser.add_argument("--dob", help="DD-MM-YYYY; if omitted, prompt securely")
        parser.add_argument("--no-download", action="store_true")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        dob = options["dob"] or getpass.getpass("DOB (DD-MM-YYYY): ")
        if not re.fullmatch(r"\d{2}-\d{2}-\d{4}", dob):
            raise CommandError("DOB must use DD-MM-YYYY format")

        opener = build_opener(HTTPCookieProcessor(CookieJar()))
        login_url, html = get_page(opener, LOGIN_URL)
        parser = PageParser(); parser.feed(html)
        action = urljoin(login_url, parser.form.get("action", "") if parser.form else login_url)
        form = dict(parser.hidden)
        def find_input(*words):
            for item in parser.inputs:
                haystack = " ".join(item.get(key, "") for key in ("name", "id", "placeholder")).lower()
                if any(word in haystack for word in words): return item["name"]
            return None

        staff_field = find_input("staff", "staffno", "staff_no")
        dob_field = find_input("dob", "birth", "dateofbirth", "date_of_birth")
        submit_field = next((item["name"] for item in parser.inputs if item.get("type", "").lower() in {"submit", "button"}), None)
        if not staff_field or not dob_field:
            raise CommandError("Could not identify the staff-number/DOB fields on the login form")
        form.update({staff_field: options["staff_no"], dob_field: dob})
        if submit_field: form[submit_field] = "Login"
        with opener.open(Request(action, data=urlencode(form).encode(), headers={"User-Agent": "BBAU private notice migration", "Content-Type": "application/x-www-form-urlencoded"}), timeout=30) as response:
            private_url = response.geturl(); private_html = response.read().decode("utf-8", "ignore")
        if "Faculty Notice Board" in private_html and "Enter Staff No" in private_html:
            raise CommandError("Login failed; check staff number and DOB or inspect the form field names")

        parser = PageParser(); parser.feed(private_html)
        records = []
        for item in parser.links:
            href = quote(urljoin(private_url, item["href"]), safe=":/?=&%#")
            title = re.sub(r"\s+", " ", item["text"]).strip()
            if not title or ".pdf" not in href.lower(): continue
            records.append((title, notice_date(item, href), href))
        self.stdout.write(f"Found {len(records)} private PDF notices")

        created = skipped = 0
        for title, posted, href in records:
            existing = GlobalNotice.objects.filter(title__iexact=title, is_private=True).first()
            if existing:
                # Correct records imported earlier with the old 01-01 fallback date.
                category = notice_category(title)
                changed = []
                if existing.date_posted != posted: existing.date_posted = posted; changed.append("date_posted")
                if existing.categories != [category]: existing.categories = [category]; changed.append("categories")
                if changed and not options["dry_run"]: existing.save(update_fields=changed)
                skipped += 1; continue
            if options["dry_run"]:
                self.stdout.write(f"{posted} | {title} | {href}"); continue
            with transaction.atomic():
                notice = GlobalNotice(title=title, date_posted=posted, categories=[notice_category(title)], is_private=True)
                if options["no_download"]:
                    notice.link = href; notice.save()
                else:
                    filename = re.sub(r"[^A-Za-z0-9._-]+", "_", title)[:100] + ".pdf"
                    temporary = Path("/tmp") / filename
                    with opener.open(Request(href, headers={"User-Agent": "BBAU private notice migration"}), timeout=60) as response:
                        content = response.read()
                    if len(content) > MAX_FILE_SIZE:
                        self.stdout.write(self.style.WARNING(f"Skipped over-20MB file: {title}"))
                        continue
                    temporary.write_bytes(content)
                    with temporary.open("rb") as handle: notice.attachment.save(filename, File(handle), save=True)
                    temporary.unlink(missing_ok=True)
            created += 1
        self.stdout.write(self.style.SUCCESS(f"Imported private notices: {created}; skipped existing: {skipped}"))
