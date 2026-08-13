from django.shortcuts import redirect
from django.urls import reverse


class ForcePasswordChangeMiddleware:
    """
    user to change their password on first login.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_superuser:
            try:
                if (
                    getattr(request.user, "portal_profile", None)
                    and request.user.portal_profile.force_password_change
                ):
                    # Paths the user is allowed to access while locked
                    allowed_paths = [
                        reverse("admin:password_change"),
                        reverse("admin:password_change_done"),
                        reverse("portal_logout"),
                        reverse("admin:logout"),  # Allow Django admin logout button
                    ]

                    # If the current path is not allowed, redirect them
                    if (
                        request.path not in allowed_paths
                        and not request.path.startswith("/static/")
                        and not request.path.startswith("/media/")
                    ):
                        return redirect("admin:password_change")
            except Exception:
                pass

        response = self.get_response(request)
        return response


from django.core.exceptions import SuspiciousOperation
import os


from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect


class FileValidationMiddleware:

    # Middleware to globally validate all file uploads and prevent malicious extensions.

    ALLOWED_EXTENSIONS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",  # Images
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".csv",
        ".txt",  # Documents
    }

    # 20 MB limit
    MAX_UPLOAD_SIZE = 20 * 1024 * 1024

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.FILES:
            for file_key in request.FILES:
                for uploaded_file in request.FILES.getlist(file_key):
                    error_msg = None

                    # 1. Check File Size
                    if uploaded_file.size > self.MAX_UPLOAD_SIZE:
                        error_msg = f"Upload Failed: File '{uploaded_file.name}' exceeds the maximum allowed size of 20MB."

                    # 2. Check File Extension
                    ext = os.path.splitext(uploaded_file.name)[1].lower()
                    if not error_msg and ext not in self.ALLOWED_EXTENSIONS:
                        error_msg = f"Upload Failed: File extension '{ext}' is not allowed for security reasons."

                    if error_msg:
                        # If this is an API request, return a JSON error
                        if request.path.startswith("/api/"):
                            return JsonResponse({"error": error_msg}, status=400)

                        # Otherwise, use Django messages for the admin/portal and redirect back
                        messages.error(request, error_msg)
                        referer = request.META.get("HTTP_REFERER", "/admin/")
                        return redirect(referer)

                    # rename the file if it had extra space or any emojis
                    import re

                    original_name = os.path.splitext(uploaded_file.name)[0]
                    safe_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", original_name)
                    # Remove double underscores
                    safe_name = re.sub(r"_+", "_", safe_name).strip("_")
                    if not safe_name:
                        safe_name = "upload"

                    uploaded_file.name = f"{safe_name}{ext}"

        return self.get_response(request)
