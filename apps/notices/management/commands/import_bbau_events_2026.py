import re
from datetime import date
from html.parser import HTMLParser
from urllib.parse import quote, urljoin
from urllib.request import Request, urlopen
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.notices.models import GlobalNotice

SOURCE_URL = "https://www.bbau.ac.in/Events.aspx"
MAX_FILE_SIZE = 20 * 1024 * 1024
MONTHS = {name.lower(): number for number, name in enumerate(
    ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"), 1
)}


class EventParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items, self.current = [], None

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.current = {"title": "", "href": dict(attrs).get("href", "")}

    def handle_data(self, data):
        if self.current is not None:
            self.current["title"] += data

    def handle_endtag(self, tag):
        if tag == "a" and self.current is not None:
            self.items.append(self.current)
            self.current = None


def event_date(title, url):
    # Examples: June 08, 2026; 15th August 2026; 05 June-2026.
    month_names = "January|February|March|April|May|June|July|August|September|October|November|December"
    patterns = [
        rf"({month_names})\s+(\d{{1,2}})(?:st|nd|rd|th)?[, .-]+2026",
        rf"(\d{{1,2}})(?:st|nd|rd|th)?\s+({month_names})[, .-]+2026",
    ]
    for index, pattern in enumerate(patterns):
        match = re.search(pattern, title, re.I)
        if match:
            month, day = (match.group(1), match.group(2)) if index == 0 else (match.group(2), match.group(1))
            return date(2026, MONTHS[month.lower()], int(day))

    # Some old PDF names carry the exact date, e.g. Eminent_Lecture_08062026.pdf.
    match = re.search(r"(?<!\d)(\d{2})(\d{2})2026(?!\d)", url)
    if match:
        first, second = int(match.group(1)), int(match.group(2))
        if 1 <= second <= 12 and 1 <= first <= 31:
            return date(2026, second, first)
        if 1 <= first <= 12 and 1 <= second <= 31:
            return date(2026, first, second)
    return date(2026, 1, 1)


class Command(BaseCommand):
    help = "Import 2026 events from the old BBAU Events page"

    def add_arguments(self, parser):
        parser.add_argument("--no-download", action="store_true")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        request = Request(SOURCE_URL, headers={"User-Agent": "BBAU event migration"})
        with urlopen(request, timeout=30) as response:
            parser = EventParser(); parser.feed(response.read().decode("utf-8", "ignore"))

        records = []
        started = False
        for item in parser.items:
            title = re.sub(r"\s+", " ", item["title"]).strip()
            href = quote(urljoin(SOURCE_URL, item["href"]), safe=":/?=&%#")
            if not title or "/conference/" not in href.lower():
                continue
            # Import only the requested 2026 block, inclusive.
            if "Minute-to-Minute Programme on 15th August 2026" in title:
                started = True
            if not started:
                continue
            if "International Women's Day will be celebrated in the University" in title:
                records.append((title, event_date(title, href), href))
                break
            records.append((title, event_date(title, href), href))

        unique = {(title.casefold(), posted): (title, posted, href) for title, posted, href in records}
        self.stdout.write(f"Found {len(unique)} unique 2026 events")
        created = skipped = 0
        for title, posted, href in unique.values():
            existing = GlobalNotice.objects.filter(title__iexact=title, date_posted=posted).first()
            if existing:
                if "Event" not in (existing.categories or []) and not options["dry_run"]:
                    existing.categories = list(dict.fromkeys((existing.categories or []) + ["Event"]))
                    existing.save(update_fields=["categories"])
                skipped += 1
                continue
            if options["dry_run"]:
                self.stdout.write(f"{posted} | {title} | {href}")
                continue
            with transaction.atomic():
                notice = GlobalNotice(title=title, date_posted=posted, categories=["Event"])
                if options["no_download"]:
                    notice.link = href
                    notice.save()
                else:
                    filename = re.sub(r"[^A-Za-z0-9._-]+", "_", title)[:100] + ".pdf"
                    temporary = Path("/tmp") / filename
                    with urlopen(Request(href, headers={"User-Agent": "BBAU event migration"}), timeout=60) as response:
                        content = response.read()
                    if len(content) > MAX_FILE_SIZE:
                        self.stdout.write(self.style.WARNING(f"Skipped over-20MB file: {title}"))
                        continue
                    temporary.write_bytes(content)
                    with temporary.open("rb") as handle:
                        notice.attachment.save(filename, File(handle), save=True)
                    temporary.unlink(missing_ok=True)
            created += 1
        self.stdout.write(self.style.SUCCESS(f"Imported: {created}; skipped existing: {skipped}"))
