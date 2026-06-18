from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

User = get_user_model()

ACCESS_COOKIE = "access_token"
REFRESH_COOKIE = "refresh_token"
COOKIE_SAMESITE = "Lax"
COOKIE_HTTPONLY = True
COOKIE_SECURE = False  # Set True in production (HTTPS only)


def set_auth_cookies(response, refresh):
    """Set HttpOnly JWT access and refresh cookies on a response."""
    opts = {"httponly": COOKIE_HTTPONLY, "samesite": COOKIE_SAMESITE, "secure": COOKIE_SECURE}
    response.set_cookie(ACCESS_COOKIE, str(refresh.access_token), **opts)
    response.set_cookie(REFRESH_COOKIE, str(refresh), **opts)


def delete_auth_cookies(response):
    """Remove both auth cookies from a response."""
    response.delete_cookie(ACCESS_COOKIE)
    response.delete_cookie(REFRESH_COOKIE)


def authenticate_user(username_or_email, password):
    """Resolve a username or email to an email, then authenticate."""
    email = username_or_email
    if "@" not in username_or_email:
        try:
            email = User.objects.get(username=username_or_email).email
        except User.DoesNotExist:
            pass
    return authenticate(username=email, password=password)


def rotate_token_if_needed(refresh):
    """Rotate the refresh token in-place if token rotation is configured."""
    from rest_framework_simplejwt.settings import api_settings
    if not api_settings.ROTATE_REFRESH_TOKENS:
        return
    if api_settings.BLACKLIST_AFTER_ROTATION:
        try:
            refresh.blacklist()
        except AttributeError:
            pass
    refresh.set_jti()
    refresh.set_exp()
    refresh.set_iat()


def blacklist_token(refresh_token_str):
    """Blacklist the given refresh token string, silently ignore errors."""
    try:
        if refresh_token_str:
            RefreshToken(refresh_token_str).blacklist()
    except (TokenError, InvalidToken):
        pass
