from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class CookieJWTAuthentication(JWTAuthentication):
    """
    Authenticates requests using the 'access_token' HttpOnly cookie
    instead of the Authorization: Bearer header.
    """

    def authenticate(self, request):
        access_token = request.COOKIES.get("access_token")
        if not access_token:
            return None

        try:
            validated_token = self.get_validated_token(access_token)
        except (InvalidToken, TokenError):
            return None

        return self.get_user(validated_token), validated_token
