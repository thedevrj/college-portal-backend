import logging
import threading
from datetime import datetime
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)

PORTAL_URL_PATHS = {
    "grievance": "/complaint-management-portal/?tab=track",
    "icc": "/internal-complaint-committee-portal/?tab=track",
    "discrimination": "/sc-st-portal/?tab=track",
    "feedback": "/student-feedback-portal/?tab=track",
    "vigilance": "/cvo-portal/?tab=track",
    "affidavit": "/affidavit-portal/#track-status",
}


def get_tracking_url(portal_slug: str, tracking_id: str) -> str:
    """
    Builds the public or frontend URL for tracking a submitted case.
    """
    raw_url = getattr(settings, "FRONTEND_PORTAL_URL", None)
    base_url = str(raw_url).rstrip("/")
    path_template = PORTAL_URL_PATHS.get(portal_slug, "/track/{tracking_id}")
    path = path_template.format(tracking_id=tracking_id)
    return f"{base_url}{path}"


def _send_email_worker(subject: str, text_content: str, html_content: str, recipient_list: list):
    """
    Worker function executed in a background thread to send email without blocking HTTP responses.
    """
    try:
        from_email = getattr(
            settings,
            "DEFAULT_FROM_EMAIL",
            "BBAU University <no-reply@bbau.ac.in>",
        )
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=recipient_list,
        )
        if html_content:
            msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        print(f"[EMAIL SERVICE] Successfully sent email '{subject}' to {recipient_list}")
        logger.info(
            "Successfully sent email '%s' to recipients: %s",
            subject,
            recipient_list,
        )
    except Exception as exc:
        print(f"[EMAIL SERVICE ERROR] Failed sending email '{subject}' to {recipient_list}: {exc}")
        logger.error(
            "Error sending email '%s' to %s: %s",
            subject,
            recipient_list,
            exc,
            exc_info=True,
        )


def _send_mail_async(subject: str, text_content: str, html_content: str, recipient_list: list):
    """
    Dispatches email sending asynchronously in a background thread.
    """
    if not recipient_list:
        logger.warning("Email dispatch skipped: no recipient provided for '%s'", subject)
        return

    # Filter out empty or whitespace-only emails
    valid_recipients = [r.strip() for r in recipient_list if r and r.strip()]
    if not valid_recipients:
        return

    thread = threading.Thread(
        target=_send_email_worker,
        args=(subject, text_content, html_content, valid_recipients),
        daemon=True,
    )
    thread.start()


def send_tracking_id_email(
    to_email: str,
    recipient_name: str,
    tracking_id: str,
    portal_name: str,
    portal_slug: str = "grievance",
    category: str = None,
    initial_status: str = "Pending",
    submitted_at: datetime = None,
):
    """
    Sends automated confirmation email with tracking ID upon form submission.
    """
    if not to_email:
        return

    if not submitted_at:
        submitted_at = timezone.now()

    if hasattr(submitted_at, "strftime"):
        formatted_date = submitted_at.strftime("%d %b %Y, %I:%M %p")
    else:
        formatted_date = str(submitted_at)

    tracking_url = get_tracking_url(portal_slug, tracking_id)

    context = {
        "recipient_name": recipient_name or "Applicant",
        "tracking_id": tracking_id,
        "portal_name": portal_name,
        "category": category,
        "initial_status": initial_status,
        "submitted_at": formatted_date,
        "tracking_url": tracking_url,
    }

    subject = f"[{portal_name}] Application Received - Tracking ID: {tracking_id}"

    try:
        html_content = render_to_string("emails/submission_confirmation.html", context)
        text_content = render_to_string("emails/submission_confirmation.txt", context)
    except Exception as exc:
        logger.error("Error rendering submission confirmation email templates: %s", exc)
        # Fallback plain text
        text_content = (
            f"Dear {recipient_name or 'Applicant'},\n\n"
            f"Your application has been received in {portal_name}.\n"
            f"Your Tracking ID is: {tracking_id}\n\n"
            f"Track Status: {tracking_url}\n\n"
            f"Babasaheb Bhimrao Ambedkar University"
        )
        html_content = None

    _send_mail_async(subject, text_content, html_content, [to_email])


def send_status_update_email(
    to_email: str,
    recipient_name: str,
    tracking_id: str,
    portal_name: str,
    portal_slug: str = "grievance",
    old_status_display: str = "Pending",
    new_status_display: str = "Updated",
    remarks: str = None,
    updated_at: datetime = None,
):
    """
    Sends automated status update email when an officer changes the status of a complaint/request.
    """
    if not to_email:
        return

    if not updated_at:
        updated_at = timezone.now()

    if hasattr(updated_at, "strftime"):
        formatted_date = updated_at.strftime("%d %b %Y, %I:%M %p")
    else:
        formatted_date = str(updated_at)

    tracking_url = get_tracking_url(portal_slug, tracking_id)

    status_lower = (new_status_display or "").lower()
    is_resolved = any(k in status_lower for k in ["resolved", "approved", "completed", "verified"])
    is_negative = any(k in status_lower for k in ["reject", "dismiss", "closed", "invalid"])

    context = {
        "recipient_name": recipient_name or "Applicant",
        "tracking_id": tracking_id,
        "portal_name": portal_name,
        "old_status_display": old_status_display or "Previous Status",
        "new_status_display": new_status_display or "Updated Status",
        "remarks": remarks.strip() if remarks else None,
        "updated_at": formatted_date,
        "tracking_url": tracking_url,
        "is_resolved": is_resolved,
        "is_negative": is_negative,
    }

    subject = f"[{portal_name}] Status Updated: {new_status_display} (ID: {tracking_id})"

    try:
        html_content = render_to_string("emails/status_update.html", context)
        text_content = render_to_string("emails/status_update.txt", context)
    except Exception as exc:
        logger.error("Error rendering status update email templates: %s", exc)
        text_content = (
            f"Dear {recipient_name or 'Applicant'},\n\n"
            f"The status of your case in {portal_name} has been updated.\n"
            f"Tracking ID: {tracking_id}\n"
            f"Status: {old_status_display} -> {new_status_display}\n"
            + (f"Remarks: {remarks}\n" if remarks else "")
            + f"\nTrack your case at: {tracking_url}\n\n"
            f"Babasaheb Bhimrao Ambedkar University"
        )
        html_content = None

    _send_mail_async(subject, text_content, html_content, [to_email])
