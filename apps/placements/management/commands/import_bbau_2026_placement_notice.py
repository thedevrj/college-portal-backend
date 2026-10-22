import email.utils
import os
import re
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, urljoin
from urllib.request import Request, urlopen

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.placements.models import PlacementNotice

SOURCE_URL = "https://www.bbau.ac.in/CPCUpdates.aspx"
MAX_FILE_SIZE = 25 * 1024 * 1024

MONTHS = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}


class CPCTableParser(HTMLParser):
    """Parses rows from the CPC Updates table (S.No, Details, Download)."""

    def __init__(self):
        super().__init__()
        self.in_tbody = False
        self.rows = []
        self.current_row = None
        self.current_cell = None

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "tbody":
            self.in_tbody = True
        elif tag == "tr" and self.in_tbody:
            self.current_row = []
        elif tag in ("td", "th") and self.current_row is not None:
            self.current_cell = {"text": "", "href": None}
        elif tag == "a" and self.current_cell is not None:
            href = attrs_dict.get("href")
            if href:
                self.current_cell["href"] = href

    def handle_data(self, data):
        if self.current_cell is not None:
            self.current_cell["text"] += data

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.current_cell is not None:
            self.current_row.append(self.current_cell)
            self.current_cell = None
        elif tag == "tr" and self.current_row is not None:
            if self.current_row:
                self.rows.append(self.current_row)
            self.current_row = None
        elif tag == "tbody":
            self.in_tbody = False


def extract_notice_date(title, href):
    """Extracts a 2026 date from title or href."""
    # 1. Date in title: DD-MM-YYYY or DD/MM/YYYY
    m = re.search(r"(\d{1,2})[-/](\d{1,2})[-/](2026)", title)
    if m:
        d, mon, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= mon <= 12 and 1 <= d <= 31:
            return date(y, mon, d)

    # 2. Date in title: Month DD, 2026
    m = re.search(
        r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})(?:st|nd|rd|th)?(?:,)?\s+2026",
        title,
        re.I,
    )
    if m:
        mon = MONTHS.get(m.group(1).lower())
        d = int(m.group(2))
        if mon and 1 <= d <= 31:
            return date(2026, mon, d)

    # 3. Date in title: DD Month 2026
    m = re.search(
        r"(\d{1,2})(?:st|nd|rd|th)?\s+(January|February|March|April|May|June|July|August|September|October|November|December)(?:,)?\s+2026",
        title,
        re.I,
    )
    if m:
        d = int(m.group(1))
        mon = MONTHS.get(m.group(2).lower())
        if mon and 1 <= d <= 31:
            return date(2026, mon, d)

    # 4. In href: DDMM2026 e.g. 13082026, 09032026
    m = re.search(r"(\d{2})(\d{2})2026", href)
    if m:
        d, mon = int(m.group(1)), int(m.group(2))
        if 1 <= mon <= 12 and 1 <= d <= 31:
            return date(2026, mon, d)

    # 5. In href: DDMM26 e.g. 220426, 130226
    m = re.search(r"[_-](\d{2})(\d{2})26(?!\d)", href)
    if m:
        d, mon = int(m.group(1)), int(m.group(2))
        if 1 <= mon <= 12 and 1 <= d <= 31:
            return date(2026, mon, d)

    # 6. In href: month name folder e.g. oct26, sep26, september 2026
    m = re.search(
        r"/(oct|sep|september|aug|august|jul|july|jun|june|may|apr|april|mar|march|feb|february|jan|january)[\s_-]*20?26",
        href,
        re.I,
    )
    if m:
        mon = MONTHS.get(m.group(1).lower())
        if mon:
            return date(2026, mon, 1)

    # 7. In href: /2026/ folder fallback without explicit date in name
    if "/2026/" in href:
        return None

    return None


class Command(BaseCommand):
    help = "Import 2026 placement and internship notices from old BBAU CPCUpdates page"

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            default=SOURCE_URL,
            help="Source URL to scrape (default: BBAU CPCUpdates.aspx)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simulate the import without downloading files or modifying database",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Limit number of notices to import",
        )

    def handle(self, *args, **options):
        source = options["source"]
        dry_run = options["dry_run"]
        limit = options["limit"]

        self.stdout.write(f"Fetching notices from: {source}")
        request = Request(source, headers={"User-Agent": "Mozilla/5.0 (BBAU migration)"})
        with urlopen(request, timeout=30) as response:
            html = response.read().decode("utf-8", "ignore")

        parser = CPCTableParser()
        parser.feed(html)

        self.stdout.write(f"Parsed {len(parser.rows)} table rows from source.")

        records = []
        for row in parser.rows:
            if len(row) < 2:
                continue

            # Cell 1 is typically title/details, Cell 2 is download link
            title = re.sub(r"\s+", " ", row[1]["text"]).strip()
            if not title or title.lower() in ("details", "notice", "s.no"):
                continue

            href = None
            for cell in row:
                if cell.get("href"):
                    href = cell["href"]
                    break

            if not href:
                continue

            # Check stop condition: transition to 2025 or older
            href_lower = href.lower()
            if any(x in href_lower for x in ("/2025/", "oct25", "sep25", "aug25", "2024", "2023")):
                break

            posted = extract_notice_date(title, href)
            full_href = quote(urljoin(source, href), safe=":/?=&%#")
            records.append((title, posted, full_href))

        # Deduplicate
        unique = {}
        for item in records:
            key = (re.sub(r"\s+", " ", item[0]).strip().casefold(), item[2])
            unique.setdefault(key, item)
        records = list(unique.values())

        if limit:
            records = records[:limit]

        self.stdout.write(f"Found {len(records)} placement notices for 2026.")

        created = 0
        skipped = 0

        for title, posted, href in records:
            # If no date was found in title or filename, inspect server's upload date (Last-Modified)
            if not posted:
                try:
                    head_req = Request(href, headers={"User-Agent": "Mozilla/5.0 (BBAU migration)"}, method="HEAD")
                    with urlopen(head_req, timeout=15) as head_resp:
                        last_mod = head_resp.headers.get("Last-Modified")
                        if last_mod:
                            posted = email.utils.parsedate_to_datetime(last_mod).date()
                except Exception:
                    pass

                # Final fallback: use current upload date
                if not posted:
                    posted = date.today()

            existing = PlacementNotice.objects.filter(title__iexact=title, date=posted).first()
            if existing:
                skipped += 1
                continue

            if dry_run:
                self.stdout.write(f"[DRY RUN] {posted} | {title[:60]} | {href}")
                created += 1
                continue

            try:
                # Download attachment
                req = Request(href, headers={"User-Agent": "Mozilla/5.0 (BBAU migration)"})
                with urlopen(req, timeout=45) as resp:
                    if not posted:
                        last_mod = resp.headers.get("Last-Modified")
                        if last_mod:
                            try:
                                posted = email.utils.parsedate_to_datetime(last_mod).date()
                            except Exception:
                                pass
                        if not posted:
                            posted = date.today()
                    content = resp.read()

                if len(content) > MAX_FILE_SIZE:
                    self.stdout.write(self.style.WARNING(f"Skipped over-size file ({len(content)} bytes): {title}"))
                    continue

                safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(href).name)
                if not safe_name.lower().endswith(".pdf"):
                    safe_name += ".pdf"

                temp_path = Path("/tmp") / safe_name
                temp_path.write_bytes(content)

                with transaction.atomic():
                    notice = PlacementNotice(title=title, date=posted)
                    with temp_path.open("rb") as handle:
                        notice.file.save(safe_name, File(handle), save=True)

                temp_path.unlink(missing_ok=True)
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Imported: {posted} - {title}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to import '{title}': {e}"))

        self.stdout.write(
            self.style.SUCCESS(f"Finished! Imported: {created}, Skipped existing: {skipped}")
        )
