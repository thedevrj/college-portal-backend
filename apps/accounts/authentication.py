from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


class CookieJWTAuthentication(JWTAuthentication):
    """
    Authenticate API requests using either:
    1. Standard 'Authorization: Bearer <token>' header
    2. HttpOnly 'access_token' cookie
    Enforces token_version check to support instant token revocation on password change and logout.
    """

    def authenticate(self, request):
        header = self.get_header(request)
        if header is not None:
            raw_token = self.get_raw_token(header)
            if raw_token is not None:
                validated_token = self.get_validated_token(raw_token)
                user = self.get_user(validated_token)
                self._check_revocation(user, validated_token)
                return user, validated_token

        raw_token = request.COOKIES.get("access_token")
        if not raw_token:
            return None

        validated_token = self.get_validated_token(raw_token.encode("utf-8"))
        user = self.get_user(validated_token)
        self._check_revocation(user, validated_token)
        return user, validated_token

    def _check_revocation(self, user, validated_token):
        if not user or not user.is_active:
            raise AuthenticationFailed("User account is disabled or inactive.")
        try:
            current_version = user.portal_profile.token_version
        except Exception:
            current_version = 0

        if validated_token.get("token_version", 0) != current_version:
            raise AuthenticationFailed("Token has been revoked.")
