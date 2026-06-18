from django.contrib.auth import get_user_model
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from .serializers import UserRegistrationSerializer, UserSerializer, LoginSerializer
from .utils import (
    set_auth_cookies, delete_auth_cookies,
    authenticate_user, rotate_token_if_needed, blacklist_token,
    REFRESH_COOKIE,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    POST /api/register/
    Register a new user. Returns a simple success message.
    """
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "User created successfully!"},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    POST /api/login/
    Authenticate user with username (or email) + password.
    Sets access_token and refresh_token as HttpOnly cookies.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate_user(
            serializer.validated_data["username"],
            serializer.validated_data["password"],
        )
        if not user:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        refresh = RefreshToken.for_user(user)
        res = Response(
            {"detail": "Login successfully!", "user": UserSerializer(user).data},
            status=status.HTTP_200_OK,
        )
        set_auth_cookies(res, refresh)
        return res


class LogoutView(APIView):
    """
    POST /api/logout/
    Blacklists the refresh token from the cookie and clears both cookies.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        blacklist_token(request.COOKIES.get(REFRESH_COOKIE))
        res = Response(
            {"detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."},
            status=status.HTTP_200_OK,
        )
        delete_auth_cookies(res)
        return res


class CookieTokenRefreshView(APIView):
    """
    POST /api/token/refresh/
    Issues a new access_token cookie using the refresh_token cookie.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.COOKIES.get(REFRESH_COOKIE)
        if not token:
            return Response({"detail": "Refresh token not found."}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            refresh = RefreshToken(token)
            rotate_token_if_needed(refresh)
            res = Response({"detail": "Token refreshed"}, status=status.HTTP_200_OK)
            set_auth_cookies(res, refresh)
            return res
        except (TokenError, InvalidToken):
            return Response({"detail": "Refresh token is invalid or expired."}, status=status.HTTP_401_UNAUTHORIZED)
