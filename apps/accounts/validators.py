import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class ComplexityPasswordValidator:

    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        errors = []
        if len(password) < self.min_length:
            errors.append(
                ValidationError(
                    _(f"Password must be at least {self.min_length} characters long."),
                    code="password_too_short",
                )
            )
        if not re.search(r"[A-Z]", password):
            errors.append(
                ValidationError(
                    _("Password must contain at least one uppercase letter (A-Z)."),
                    code="password_no_uppercase",
                )
            )
        if not re.search(r"[a-z]", password):
            errors.append(
                ValidationError(
                    _("Password must contain at least one lowercase letter (a-z)."),
                    code="password_no_lowercase",
                )
            )
        if not re.search(r"[0-9]", password):
            errors.append(
                ValidationError(
                    _("Password must contain at least one digit (0-9)."),
                    code="password_no_number",
                )
            )
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append(
                ValidationError(
                    _(
                        "Password must contain at least one special character (!@#$%^&* etc.)."
                    ),
                    code="password_no_symbol",
                )
            )

        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        return _(
            "Your password must be at least 8 characters long and contain at least "
            "one uppercase letter, one lowercase letter, one digit, and one special character."
        )
