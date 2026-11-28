from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme


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
                        reverse("admin:logout"),
                        reverse("api_change_password"),
                    ]

                    # If the current path is not allowed, redirect them
                    if (
                        request.path not in allowed_paths
                        and not request.path.startswith("/static/")
                        and not request.path.startswith("/media/")
                    ):
                        if request.path.startswith("/api/") or request.path.startswith("/portal/api/"):
                            from django.http import JsonResponse
                            return JsonResponse(
                                {
                                    "error": "Password change required before proceeding.",
                                    "force_password_change": True,
                                },
                                status=403,
                            )
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

    ALLOWED_EXTENSIONS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp", 
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".txt", 
    }

    MAGIC_SIGNATURES = {
        ".pdf": [b"%PDF-"],
        ".png": [b"\x89PNG\r\n\x1a\n"],
        ".jpg": [b"\xff\xd8\xff"],
        ".jpeg": [b"\xff\xd8\xff"],
        ".webp": [b"RIFF"],
        ".docx": [b"PK\x03\x04"],
        ".xlsx": [b"PK\x03\x04"],
        ".pptx": [b"PK\x03\x04"],
        ".doc": [b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"],
        ".xls": [b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"],
        ".ppt": [b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"],
    }

    DANGEROUS_PAYLOADS = [
        b"MZ",              # Windows PE executable
        b"\x7fELF",         # Linux executable
        b"#!/",             # Shell script
        b"<?php",           # PHP script
        b"<script",         # Injected JavaScript
        b"<!doctype html",  # HTML document
        b"<html",           # HTML root
    ]

    # 20 MB limit
    MAX_UPLOAD_SIZE = 20 * 1024 * 1024

    def __init__(self, get_response):
        self.get_response = get_response

    def _validate_content(self, uploaded_file, ext):
        try:
            pos = uploaded_file.tell()
        except Exception:
            pos = 0

        header = uploaded_file.read(512)
        uploaded_file.seek(pos)

        header_lower = header.lower()
        for dangerous in self.DANGEROUS_PAYLOADS:
            if header_lower.startswith(dangerous.lower()):
                return f"Upload Failed: File '{uploaded_file.name}' contains disallowed script/executable content."

        # Check expected magic bytes
        signatures = self.MAGIC_SIGNATURES.get(ext)
        if signatures:
            if not any(header.startswith(sig) for sig in signatures):
                return f"Upload Failed: File content for '{uploaded_file.name}' does not match the file extension '{ext}'."

        # Text files cannot contain binary null bytes
        if ext == ".txt":
            if b"\x00" in header:
                return f"Upload Failed: Text file '{uploaded_file.name}' contains binary data."

        # Image deep verification via Pillow
        if ext in {".jpg", ".jpeg", ".png", ".webp"}:
            try:
                from PIL import Image
                img = Image.open(uploaded_file)
                img.verify()
                uploaded_file.seek(pos)
            except Exception:
                uploaded_file.seek(pos)
                return f"Upload Failed: Image file '{uploaded_file.name}' is corrupted or invalid."

        return None

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

                    # 3. Check Binary Magic Bytes & Content
                    if not error_msg:
                        error_msg = self._validate_content(uploaded_file, ext)

                    if error_msg:
                        # If this is an API request, return a JSON error
                        if request.path.startswith("/api/"):
                            return JsonResponse({"error": error_msg}, status=400)

                        # Otherwise, use Django messages for the admin/portal and redirect back
                        messages.error(request, error_msg)
                        referer = request.META.get("HTTP_REFERER")
                        is_safe_redirect = False
                        if referer:
                            try:
                                is_safe_redirect = url_has_allowed_host_and_scheme(
                                    url=referer,
                                    allowed_hosts={request.get_host()},
                                    require_https=request.is_secure(),
                                )
                            except Exception:
                                is_safe_redirect = False

                        return redirect(referer if is_safe_redirect else "/admin/")

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
