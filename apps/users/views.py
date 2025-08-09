from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from django.shortcuts import get_object_or_404

from .models import User
from .serializers import UserRegistrationSerializer, CustomTokenObtainPairSerializer, UserSerializer
from apps.core.utils import send_verification_email

class UserRegistrationView(generics.CreateAPIView):
    """
    US1: User Registration for 'applicant' or 'company'.
    Sends a verification email upon successful registration.
    """
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Send verification email
        send_verification_email(user, request)

        return Response({
            "success": True,
            "message": "Registration successful. Please check your email to verify your account.",
            "object": UserSerializer(user).data,
            "errors": None
        }, status=status.HTTP_201_CREATED)

class EmailVerificationView(views.APIView):
    """
    US2: Email Verification.
    Verifies user's email with a time-limited token.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        token = request.query_params.get('token')
        if not token:
            return Response({"success": False, "message": "Token not provided.", "object": None, "errors": ["Token is required."]}, status=status.HTTP_400_BAD_REQUEST)

        signer = TimestampSigner()
        try:
            user_id = signer.unsign(token, max_age=3600) # 1 hour expiry
            user = get_object_or_404(User, id=user_id)

            if user.is_verified:
                return Response({"success": True, "message": "Email is already verified.", "object": None, "errors": None}, status=status.HTTP_200_OK)

            user.is_verified = True
            user.is_active = True
            user.save()

            return Response({"success": True, "message": "Email verified successfully. You can now log in.", "object": None, "errors": None}, status=status.HTTP_200_OK)

        except SignatureExpired:
            # Resend email if token is expired
            user_id = signer.unsign(token, max_age=86400) # Allow reading expired token to find user
            user = get_object_or_404(User, id=user_id)
            if not user.is_verified:
                send_verification_email(user, request)
                return Response({"success": False, "message": "Token expired. A new verification link has been sent to your email.", "object": None, "errors": ["Token has expired."]}, status=status.HTTP_400_BAD_REQUEST)
            else:
                 return Response({"success": True, "message": "Email is already verified.", "object": None, "errors": None}, status=status.HTTP_200_OK)


        except BadSignature:
            return Response({"success": False, "message": "Invalid or malformed token.", "object": None, "errors": ["Invalid token."]}, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    US2: User Login.
    Returns JWT access and refresh tokens in the base response format.
    """
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            return Response({
                "success": True,
                "message": "Login successful.",
                "object": response.data,
                "errors": None
            })
        return response # The custom exception handler will format the error