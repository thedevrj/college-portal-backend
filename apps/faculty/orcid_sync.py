import logging
import urllib.request
import json
from datetime import date
from django.apps import apps

logger = logging.getLogger(__name__)


def parse_orcid_date(date_dict, default_month="01", default_day="01"):
    """
    Safely parses ORCID date dictionary and returns a python date object.
    Defaults missing month/day if only the year is available.
    """
    if not date_dict:
        return None

    year_val = date_dict.get("year")
    year = year_val.get("value") if year_val else None

    month_val = date_dict.get("month")
    month = month_val.get("value") if month_val else default_month

    day_val = date_dict.get("day")
    day = day_val.get("value") if day_val else default_day

    if year:
        try:
            return date(int(year), int(month or 1), int(day or 1))
        except Exception:
            pass
    return None


def sync_faculty_orcid(faculty):
    """
    Synchronizes a faculty member's bio, qualifications, publications, patents,
    research projects, and memberships with ORCID.
    """
    if not faculty.orcid_id:
        return {"success": False, "message": f"Faculty {faculty.name} has no ORCID ID."}

    orcid_id = faculty.orcid_id.strip()
    headers = {"Accept": "application/vnd.orcid+json"}

    # ----------------------------------------------------
    # 1. Fetch Biography
    # ----------------------------------------------------
    bio_updated = False
    person_url = f"https://pub.orcid.org/v3.0/{orcid_id}/person"
    try:
        req = urllib.request.Request(person_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status == 200:
                person_data = json.loads(response.read().decode("utf-8"))
                biography_data = person_data.get("biography")
                bio_content = biography_data.get("content") if biography_data else None
                if bio_content and bio_content.strip():
                    cleaned_orcid_bio = bio_content.strip()
                    current_bio = faculty.bio.strip() if faculty.bio else ""
                    if cleaned_orcid_bio != current_bio:
                        faculty.bio = cleaned_orcid_bio
                        faculty.save(update_fields=["bio"])
                        bio_updated = True
            else:
                logger.warning(
                    f"Failed to fetch ORCID person details for {orcid_id}: {response.status}"
                )
    except Exception as e:
        logger.error(f"Error fetching ORCID biography for {faculty.name}: {str(e)}")

    # ----------------------------------------------------
    # 2. Fetch Qualifications & Educations
    # ----------------------------------------------------
    qualifications_updated = False
    educations_url = f"https://pub.orcid.org/v3.0/{orcid_id}/educations"
    try:
        req = urllib.request.Request(educations_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status == 200:
                edu_data = json.loads(response.read().decode("utf-8"))
                groups = edu_data.get("affiliation-group", [])
                edu_records = []
                for group in groups:
                    summaries = group.get("summaries", [])
                    for summary in summaries:
                        edu_summary = summary.get("education-summary", {})
                        if not edu_summary:
                            continue
                        role_title = edu_summary.get("role-title")
                        dept_name = edu_summary.get("department-name")
                        org_name = edu_summary.get("organization", {}).get("name")

                        start_date = parse_orcid_date(edu_summary.get("start-date"))
                        end_date = parse_orcid_date(edu_summary.get("end-date"))

                        if not org_name or not role_title:
                            continue

                        dates_str = ""
                        if start_date or end_date:
                            start_year = start_date.year if start_date else ""
                            end_year = end_date.year if end_date else "Present"
                            dates_str = (
                                f" ({start_year} - {end_year})"
                                if start_year
                                else f" (Graduated {end_year})"
                            )

                        dept_str = f", {dept_name}" if dept_name else ""
                        edu_records.append(
                            f"<li><strong>{role_title}</strong>{dept_str} from {org_name}{dates_str}</li>"
                        )

                if edu_records:
                    edu_html = "<ul>\n" + "\n".join(edu_records) + "\n</ul>"
                    current_qualification = (
                        faculty.qualification.strip() if faculty.qualification else ""
                    )
                    if edu_html.strip() != current_qualification:
                        faculty.qualification = edu_html
                        faculty.save(update_fields=["qualification"])
                        qualifications_updated = True
    except Exception as e:
        logger.error(f"Error fetching ORCID educations for {faculty.name}: {str(e)}")

    # ----------------------------------------------------
    # 3. Fetch Works (Publications / Patents)
    # ----------------------------------------------------
    works_url = f"https://pub.orcid.org/v3.0/{orcid_id}/works"
    publications_added = 0
    patents_added = 0
    try:
        req = urllib.request.Request(works_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status == 200:
                works_data = json.loads(response.read().decode("utf-8"))
                groups = works_data.get("group", [])

                Publication = apps.get_model("research", "Publication")
                Patent = apps.get_model("research", "Patent")

                for group in groups:
                    summaries = group.get("work-summary", [])
                    if not summaries:
                        continue

                    # Take the first work summary in the group
                    work_summary = summaries[0]

                    title_dict = work_summary.get("title")
                    title_val = None
                    if title_dict:
                        inner_title = title_dict.get("title")
                        if inner_title:
                            title_val = inner_title.get("value")
                    if not title_val:
                        continue

                    work_type = work_summary.get("type")
                    pub_date = parse_orcid_date(work_summary.get("publication-date"))

                    doi_val = None
                    ext_ids_data = work_summary.get("external-ids")
                    ext_ids = (
                        ext_ids_data.get("external-id", []) if ext_ids_data else []
                    )
                    for ext_id in ext_ids:
                        if ext_id.get("external-id-type") == "doi":
                            doi_val = ext_id.get("external-id-value")
                            break

                    # Handle Patent
                    if work_type == "patent":
                        # Check if patent already exists
                        patent_exists = Patent.objects.filter(
                            internal_inventors=faculty, title__iexact=title_val
                        ).exists()
                        if not patent_exists:
                            patent_number = None
                            # Look for patent number in external-ids
                            for ext_id in ext_ids:
                                if ext_id.get("external-id-type") in [
                                    "patent",
                                    "other-id",
                                ]:
                                    patent_number = ext_id.get("external-id-value")
                                    break

                            patent = Patent.objects.create(
                                title=title_val,
                                patent_number=patent_number,
                                status="Granted",
                                date_of_filing=pub_date,
                                description=f"Imported from ORCID (Type: patent)",
                            )
                            PatentAuthor = apps.get_model("research", "PatentAuthor")
                            PatentAuthor.objects.create(
                                patent=patent,
                                faculty=faculty,
                                author_order=1,
                                author_role="Main Inventor"
                            )
                            patents_added += 1
                    else:
                        pub_type = "Others"
                        other_pub_type = None

                        if work_type == "journal-article":
                            pub_type = "Journal Paper"
                        elif work_type in [
                            "conference-paper",
                            "conference-poster",
                            "conference-abstract",
                        ]:
                            pub_type = "Conference Paper"
                        elif work_type == "book":
                            pub_type = "Book"
                        elif work_type == "book-chapter":
                            pub_type = "Book Chapter"
                        else:
                            pub_type = "Others"
                            other_pub_type = work_type or "ORCID Work"

                        pub_exists = False
                        if doi_val:
                            pub_exists = Publication.objects.filter(
                                internal_authors=faculty, doi_url__icontains=doi_val
                            ).exists()
                        if not pub_exists:
                            pub_exists = Publication.objects.filter(
                                internal_authors=faculty, title__iexact=title_val
                            ).exists()

                        if not pub_exists:
                            journal_title = work_summary.get("journal-title")
                            journal_name = (
                                journal_title.get("value") if journal_title else None
                            )

                            pub = Publication.objects.create(
                                title=title_val,
                                campus=faculty.campus or "BBAU",
                                publication_type=pub_type,
                                other_publication_type=other_pub_type,
                                name_of_journal_or_conference_or_publisher=journal_name,
                                publication_date=pub_date,
                                doi_url=(
                                    f"https://doi.org/{doi_val}" if doi_val else None
                                ),
                                indexing="Others",
                                others_indexing="Imported from ORCID",
                            )
                            PublicationAuthor = apps.get_model("research", "PublicationAuthor")
                            PublicationAuthor.objects.create(
                                publication=pub,
                                faculty=faculty,
                                author_order=1,
                                author_role="Main Author"
                            )
                            publications_added += 1
            else:
                logger.warning(
                    f"Failed to fetch ORCID works for {orcid_id}: {response.status}"
                )
    except Exception as e:
        logger.error(f"Error fetching ORCID works for {faculty.name}: {str(e)}")

    # ----------------------------------------------------
    # 4. Fetch Fundings (Research Projects)
    # ----------------------------------------------------
    projects_added = 0
    fundings_url = f"https://pub.orcid.org/v3.0/{orcid_id}/fundings"
    try:
        req = urllib.request.Request(fundings_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status == 200:
                funding_data = json.loads(response.read().decode("utf-8"))
                groups = funding_data.get("group", [])

                ResearchProject = apps.get_model("research", "ResearchProject")

                for group in groups:
                    summaries = group.get("funding-summary", [])
                    if not summaries:
                        continue

                    funding_summary = summaries[0]

                    title_dict = funding_summary.get("funding-title")
                    title_val = None
                    if title_dict:
                        title_val = title_dict.get("title", {}).get("value")
                    if not title_val:
                        continue

                    org_name = funding_summary.get("organization", {}).get("name")

                    proj_exists = ResearchProject.objects.filter(
                        principal_investigator=faculty, title__iexact=title_val
                    ).exists()

                    if not proj_exists and faculty.department:
                        amount_dict = funding_summary.get("amount")
                        amount_val = None
                        if amount_dict:
                            try:
                                amount_val = float(amount_dict.get("value"))
                            except (TypeError, ValueError):
                                pass

                        start_date = parse_orcid_date(funding_summary.get("start-date"))
                        end_date = parse_orcid_date(funding_summary.get("end-date"))

                        status = "Ongoing"
                        if end_date and end_date < date.today():
                            status = "Completed"

                        agency_choice = "Others"
                        others_agency = org_name

                        if org_name:
                            org_upper = org_name.upper()
                            for agency in [
                                "DST",
                                "UGC",
                                "DRDO",
                                "ICMR",
                                "ISRO",
                                "NHRC",
                                "ICSSR",
                            ]:
                                if agency in org_upper:
                                    agency_choice = agency
                                    others_agency = None
                                    break

                        ResearchProject.objects.create(
                            principal_investigator=faculty,
                            department=faculty.department,
                            title=title_val,
                            campus=faculty.campus or "BBAU",
                            funding_agency=agency_choice,
                            others_funding_agency=others_agency,
                            amount_sanctioned=amount_val,
                            start_date=start_date,
                            end_date=end_date,
                            status=status,
                            description=f"Imported from ORCID (Type: funding)",
                        )
                        projects_added += 1
    except Exception as e:
        logger.error(f"Error fetching ORCID fundings for {faculty.name}: {str(e)}")

    # ----------------------------------------------------
    # 5. Fetch Memberships & Services
    # ----------------------------------------------------
    memberships_added = 0
    memberships_url = f"https://pub.orcid.org/v3.0/{orcid_id}/memberships"
    try:
        req = urllib.request.Request(memberships_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status == 200:
                mem_data = json.loads(response.read().decode("utf-8"))
                groups = mem_data.get("affiliation-group", [])

                Membership = apps.get_model("faculty", "Membership")

                for group in groups:
                    summaries = group.get("summaries", [])
                    for summary in summaries:
                        mem_summary = summary.get("membership-summary", {})
                        if not mem_summary:
                            continue

                        role_title = mem_summary.get("role-title")
                        org_name = mem_summary.get("organization", {}).get("name")
                        if not org_name:
                            continue

                        mem_name = (
                            f"{role_title}, {org_name}" if role_title else org_name
                        )

                        mem_exists = Membership.objects.filter(
                            faculty=faculty, name__iexact=mem_name
                        ).exists()

                        if not mem_exists:
                            start_date = parse_orcid_date(mem_summary.get("start-date"))
                            end_date = parse_orcid_date(mem_summary.get("end-date"))

                            order_no = None
                            ext_ids_data = mem_summary.get("external-ids")
                            ext_ids = (
                                ext_ids_data.get("external-id", [])
                                if ext_ids_data
                                else []
                            )
                            for ext_id in ext_ids:
                                order_no = ext_id.get("external-id-value")
                                if order_no:
                                    break

                            Membership.objects.create(
                                faculty=faculty,
                                name=mem_name,
                                order_no=order_no,
                                start_date=start_date,
                                end_date=end_date,
                            )
                            memberships_added += 1
    except Exception as e:
        logger.error(f"Error fetching ORCID memberships for {faculty.name}: {str(e)}")

    msg = (
        f"Successfully synced profile for {faculty.name}. "
        f"Bio updated: {bio_updated}. "
        f"Qualifications updated: {qualifications_updated}. "
        f"Publications added: {publications_added}. "
        f"Patents added: {patents_added}. "
        f"Projects added: {projects_added}. "
        f"Memberships added: {memberships_added}."
    )
    return {
        "success": True,
        "bio_updated": bio_updated,
        "qualifications_updated": qualifications_updated,
        "publications_added": publications_added,
        "patents_added": patents_added,
        "projects_added": projects_added,
        "memberships_added": memberships_added,
        "message": msg,
    }
