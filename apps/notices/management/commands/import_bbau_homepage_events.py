import re
from datetime import date
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, urljoin
from urllib.request import Request, urlopen

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.notices.models import GlobalNotice

SOURCE_URL = "https://www.bbau.ac.in/index.aspx"
MAX_FILE_SIZE = 20 * 1024 * 1024


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.links = []; self.current = None

    def handle_starttag(self, tag, attrs):
        if tag == "a": self.current = {"text": "", "href": dict(attrs).get("href", "")}

    def handle_data(self, data):
        if self.current is not None: self.current["text"] += data

    def handle_endtag(self, tag):
        if tag == "a" and self.current is not None:
            self.links.append(self.current); self.current = None


def event_date(title, url):
    months = "January|February|March|April|May|June|July|August|September|October|November|December"
    match = re.search(rf"({months})\s+(\d{{1,2}})(?:st|nd|rd|th)?[, .-]+(2026)", title, re.I)
    if match:
        month = list(re.compile(months, re.I).finditer(match.group(1)))[0].group(0)
        return date(2026, ("january february march april may june july august september october november december".split().index(month.lower()) + 1), int(match.group(2)))
    match = re.search(r"(\d{1,2})[./-](\d{1,2})[./-](2026)", title + " " + url)
    if match: return date(2026, int(match.group(2)), int(match.group(1)))
    return date(2026, 1, 1)


def linked_event_date(url):
    if ".pdf" in url.lower() or "youtube.com" in url.lower(): return None
    try:
        with urlopen(Request(url, headers={"User-Agent": "BBAU homepage event migration"}), timeout=20) as response:
            html = response.read().decode("utf-8", "ignore")
        match = re.search(r"(\d{1,2})[./-](\d{1,2})[./-](2026)", html)
        if match: return date(2026, int(match.group(2)), int(match.group(1)))
        match = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})(?:st|nd|rd|th)?[, .-]+2026", html, re.I)
        if match:
            months = "january february march april may june july august september october november december".split()
            return date(2026, months.index(match.group(1).lower()) + 1, int(match.group(2)))
    except Exception:
        return None
    return None


def uploaded_date(url):
    try:
        request = Request(url, method="HEAD", headers={"User-Agent": "BBAU homepage event migration"})
        with urlopen(request, timeout=20) as response:
            value = response.headers.get("Last-Modified")
        if value:
            return parsedate_to_datetime(value).date()
    except Exception:
        return None
    return None


class Command(BaseCommand):
    help = "Import only the homepage Events / Announcement block"

    def add_arguments(self, parser):
        parser.add_argument("--no-download", action="store_true")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        with urlopen(Request(SOURCE_URL, headers={"User-Agent": "BBAU homepage event migration"}), timeout=30) as response:
            parser = LinkParser(); parser.feed(response.read().decode("utf-8", "ignore"))

        records, active = [], False
        for item in parser.links:
            title = re.sub(r"\s+", " ", item["text"]).strip()
            if "Events / Announcement" in title:
                active = True; continue
            if active and title.lower() == "more..": break
            if not active or not title or title.lower() in {"home", "latest news"}: continue
            href = quote(urljoin(SOURCE_URL, item["href"]), safe=":/?=&%#")
            if ".pdf" not in href.lower() and "youtube.com" in href.lower(): continue
            posted = event_date(title, href)
            if posted == date(2026, 1, 1):
                posted = linked_event_date(href) or uploaded_date(href) or posted
            records.append((title, posted, href))

        unique = {(title.casefold(), posted): (title, posted, href) for title, posted, href in records}
        self.stdout.write(f"Found {len(unique)} homepage events")
        created = skipped = 0
        for title, posted, href in unique.values():
            existing = GlobalNotice.objects.filter(title__iexact=title).first()
            if existing:
                changed = []
                if posted != date(2026, 1, 1) and existing.date_posted != posted:
                    existing.date_posted = posted; changed.append("date_posted")
                if "Event" not in (existing.categories or []):
                    existing.categories = list(dict.fromkeys((existing.categories or []) + ["Event"])); changed.append("categories")
                if changed and not options["dry_run"]: existing.save(update_fields=changed)
                skipped += 1; continue
            if options["dry_run"]:
                self.stdout.write(f"{posted} | {title} | {href}"); continue
            with transaction.atomic():
                notice = GlobalNotice(title=title, date_posted=posted, categories=["Event"])
                if options["no_download"]:
                    notice.link = href; notice.save()
                else:
                    filename = re.sub(r"[^A-Za-z0-9._-]+", "_", title)[:100] + ".pdf"
                    temporary = Path("/tmp") / filename
                    with urlopen(Request(href, headers={"User-Agent": "BBAU homepage event migration"}), timeout=60) as response:
                        content = response.read()
                    if len(content) > MAX_FILE_SIZE:
                        self.stdout.write(self.style.WARNING(f"Skipped over-20MB file: {title}")); continue
                    temporary.write_bytes(content)
                    with temporary.open("rb") as handle: notice.attachment.save(filename, File(handle), save=True)
                    temporary.unlink(missing_ok=True)
            created += 1
        self.stdout.write(self.style.SUCCESS(f"Imported: {created}; skipped existing: {skipped}"))
