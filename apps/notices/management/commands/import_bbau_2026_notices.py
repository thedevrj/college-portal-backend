import re
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, urljoin
from urllib.request import Request, urlopen

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.notices.models import GlobalNotice


SOURCE_URL = "https://www.bbau.ac.in/PublicNotices.aspx"
MAX_FILE_SIZE = 20 * 1024 * 1024


class NoticeTableParser(HTMLParser):
    """Reads rows from the old site's Notice/Date table."""
    def __init__(self):
        super().__init__()
        self.rows, self.row, self.cell, self.anchor = [], None, None, None
        self.loose_anchor = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "tr": self.row = []
        elif tag in ("td", "th") and self.row is not None: self.cell = {"text": "", "href": None}
        elif tag == "a" and self.cell is not None:
            self.anchor = attrs.get("href")
            if self.anchor: self.cell["href"] = self.anchor
        elif tag == "a" and self.cell is None:
            self.loose_anchor = {"text": "", "href": attrs.get("href")}

    def handle_data(self, data):
        if self.cell is not None: self.cell["text"] += data
        elif self.loose_anchor is not None: self.loose_anchor["text"] += data

    def handle_endtag(self, tag):
        if tag == "a":
            if self.cell is None and self.loose_anchor is not None:
                self.rows.append([self.loose_anchor])
                self.loose_anchor = None
            self.anchor = None
        elif tag in ("td", "th") and self.cell is not None:
            self.row.append(self.cell); self.cell = None
        elif tag == "tr" and self.row:
            self.rows.append(self.row); self.row = None


def category_for(title):
    text = title.lower()
    if any(x in text for x in ("admission", "merit list", "counselling", "counseling", "prospectus")):
        return "Announcement"
    if any(x in text for x in ("interview", "appointment", "faculty", "research assistant", "professor")):
        return "Appointment"
    if any(x in text for x in ("tender", "quotation")):
        return "Tenders"
    if any(x in text for x in ("programme", "program", "jayanti", "workshop", "meeting")):
        return "Event"
    return "Announcement"


class Command(BaseCommand):
    help = "Import 2026 public notices from the old BBAU website"

    def add_arguments(self, parser):
        parser.add_argument("--source", action="append", help="Source URL; may be supplied more than once")
        parser.add_argument("--no-download", action="store_true", help="Keep old PDF URL in link instead of downloading")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        records = []
        # This command is intentionally limited to the Public Notices page.
        sources = options["source"] or [SOURCE_URL]
        for source in sources:
            request = Request(source, headers={"User-Agent": "BBAU notice migration"})
            with urlopen(request, timeout=30) as response:
                parser = NoticeTableParser(); parser.feed(response.read().decode("utf-8", "ignore"))
            force_event = "events.aspx" in source.lower()
            event_2025_started = False
            for row in parser.rows:
                if force_event:
                    row_title = re.sub(r"\s+", " ", row[0]["text"]).strip() if row else ""
                    if "2025" in row_title:
                        event_2025_started = True
                    if event_2025_started:
                        continue
                self._collect_row(records, row, source, force_event)

        # The two old pages can contain the same item. Keep one copy.
        unique = {}
        for item in records:
            key = (re.sub(r"\s+", " ", item[0]).strip().casefold(), item[1])
            unique.setdefault(key, item)
        records = list(unique.values())

        self.stdout.write(f"Found {len(records)} unique notices/events dated in 2026")
        created = skipped = 0
        for title, posted, href, forced_category in records:
            existing = GlobalNotice.objects.filter(title__iexact=title, date_posted=posted).first()
            if existing:
                # If an existing item has no category, enrich it instead of creating a duplicate.
                if forced_category == "Event" and "Event" not in (existing.categories or []):
                    existing.categories = list(dict.fromkeys((existing.categories or []) + ["Event"]))
                    if not options["dry_run"]: existing.save(update_fields=["categories"])
                skipped += 1; continue
            if options["dry_run"]:
                self.stdout.write(f"{posted} | {title} | {href or '-'}"); continue
            with transaction.atomic():
                notice = GlobalNotice(title=title, date_posted=posted, categories=[forced_category or category_for(title)])
                if options["no_download"] or not href:
                    notice.link = href
                    notice.save()
                else:
                    pdf = Path("/tmp") / (re.sub(r"[^A-Za-z0-9._-]+", "_", title)[:100] + ".pdf")
                    with urlopen(Request(href, headers={"User-Agent": "BBAU notice migration"}), timeout=60) as response:
                        content = response.read()
                    if len(content) > MAX_FILE_SIZE:
                        self.stdout.write(self.style.WARNING(f"Skipped over-20MB file: {title}"))
                        continue
                    pdf.write_bytes(content)
                    with pdf.open("rb") as handle:
                        notice.attachment.save(pdf.name, File(handle), save=True)
                    pdf.unlink(missing_ok=True)
            created += 1
        self.stdout.write(self.style.SUCCESS(f"Imported: {created}; skipped/enriched existing: {skipped}"))

    def _collect_row(self, records, row, source, force_event):
        if len(row) < 1 or (len(row) < 2 and not force_event): return
        title = re.sub(r"\s+", " ", row[0]["text"]).strip()
        href = next((c["href"] for c in row if c["href"]), None)
        if href: href = quote(urljoin(source, href), safe=":/?=&%#")
        raw_date = row[-1]["text"].strip()
        match = re.search(r"(\d{2})[-/]([01]\d)[-/](2026)", raw_date)
        if force_event and not match:
            month_names = "January|February|March|April|May|June|July|August|September|October|November|December"
            month_first = re.search(rf"({month_names})\s+(\d{{1,2}})(?:st|nd|rd|th)?[, .-]+2026", title, re.I)
            day_first = re.search(rf"(\d{{1,2}})(?:st|nd|rd|th)?\s+({month_names})[, .-]+2026", title, re.I)
            if month_first or day_first:
                months = {name.lower(): number for number, name in enumerate(("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"), 1)}
                parsed = month_first or day_first
                month_name, day = (parsed.group(1), parsed.group(2)) if month_first else (parsed.group(2), parsed.group(1))
                posted = date(2026, months[month_name.lower()], int(day))
                match = True
            else:
                filename_date = re.search(r"(?<!\d)(\d{2})(\d{2})2026(?!\d)", href or "")
                if filename_date:
                    posted = date(2026, int(filename_date.group(2)), int(filename_date.group(1)))
                    match = True
                else:
                    posted = date(2026, 1, 1)
        else:
            posted = None
        if (not match and not force_event) or not title or title.lower() in {"notice", "date"}: return
        if force_event and ("/conference/" not in (href or "").lower()): return
        if posted is None: posted = date(2026, int(match.group(2)), int(match.group(1)))
        records.append((title, posted, href, "Event" if force_event else None))
