from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """Authenticate API requests using the HttpOnly access-token cookie."""

    def authenticate(self, request):
        raw_token = request.COOKIES.get("access_token")
        if not raw_token:
            return super().authenticate(request)

        validated_token = self.get_validated_token(raw_token.encode("utf-8"))
        return self.get_user(validated_token), validated_token
