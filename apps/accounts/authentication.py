from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


class CookieJWTAuthentication(JWTAuthentication):
    """Authenticate API requests using the HttpOnly access-token cookie."""

    def authenticate(self, request):
        raw_token = request.COOKIES.get("access_token")
        if not raw_token:
            return super().authenticate(request)

        validated_token = self.get_validated_token(raw_token.encode("utf-8"))
        user = self.get_user(validated_token)
        try:
            current_version = user.portal_profile.token_version
        except Exception:
            current_version = 0
        if validated_token.get("token_version", 0) != current_version:
            raise AuthenticationFailed("Token has been revoked.")
        return user, validated_token
