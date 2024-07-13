from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from shared.utility import send_email, check_email_or_phone
from .serializers import SignUpSerializer, ChangeUserInformation, ChangeUserPhotoSerializer, LoginSerializer, \
    LoginRefreshSerializer, LogoutSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
from .models import User, NEW, CODE_VERIFIED, VIA_EMAIL, VIA_PHONE


class CreateUserView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = SignUpSerializer


class VerifyAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        code = self.request.data.get('code')

        self.check_verify(user, code)
        return Response(
            data={'success': True,
                  'auth_status': user.auth_status,
                  'access': user.token()['access'],
                  'refresh': user.token()['refresh_token'],
                  }
        )

    @staticmethod
    def check_verify(user, code):
        verifies = user.verify_codes.filter(expiration_time__gte=datetime.now(), code=code, is_confirmed=False)
        if not verifies.exists():
            data = {
                'message': 'Your confirmation code is invalid or expired',
            }
            raise ValidationError(data)
        else:
            verifies.update(is_confirmed=True)
        if user.auth_status == NEW:
            user.auth_status = CODE_VERIFIED
            user.save()
        return True


class NewVerifyCodeAPIView(APIView):
    def get(self, request, *args, **kwargs):
        user = self.request.user
        self.check_verification(user)
        if user.auth_types == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            send_email(user.email, code)
        elif user.auth_types == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            send_email(user.phone_number, code)
        else:
            data = {
                'message': 'Email or Phone number is not valid'
            }
            raise ValidationError(data)
        return Response(
            data={'success': True,
                  'message': 'Your verification code sent again!'}
        )

    @staticmethod
    def check_verification(user):
        verifies = user.verify_codes.filter(expiration_time__gte=datetime.now(), is_confirmed=False)
        if verifies.exists():
            data = {
                'message': 'Your confirmation code is not expired, please wait a few minutes',
            }
            raise ValidationError(data)


class ChangeUserInformationView(UpdateAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = ChangeUserInformation
    http_method_names = ['put', 'patch', 'delete']

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        super(ChangeUserInformationView, self).update(request, *args, **kwargs)
        data = {'success': True,
                'message': 'User information updated successfully',
                'auth_status': self.request.user.auth_status, }
        return Response(
            data, status=status.HTTP_200_OK
        )

    def partial_update(self, request, *args, **kwargs):
        super(ChangeUserInformationView, self).partial_update(request, *args, **kwargs)
        data = {'success': True,
                'message': 'User information updated successfully',
                'auth_status': self.request.user.auth_status, }
        return Response(
            data, status=status.HTTP_200_OK
        )


class ChangeUserPhotoView(APIView):
    permission_classes = [IsAuthenticated, ]

    def put(self, request, *args, **kwargs):
        serializer = ChangeUserPhotoSerializer(data=request.data)
        if serializer.is_valid():
            user = self.request.user
            serializer.update(user, serializer.validated_data)
            data = {'success': True,
                    'message': "User's photo updated successfully", }
            return Response(
                data, status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class LoginRefreshView(TokenRefreshView):
    serializer_class = LoginRefreshSerializer


class LogoutView(APIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = self.request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            data = {'success': True,
                    'message': 'Logged out successfully', }
            return Response(data, status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            data = {'success': False,
                    'message': 'Invalid refresh token'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordAPIView(APIView):
    permission_classes = [AllowAny, ]
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        email_or_phone = serializer.validated_data.get('email_or_phone')
        user = serializer.validated_data.get('user')
        if check_email_or_phone(email_or_phone) == 'phone':
            code = user.create_verify_code(VIA_PHONE)
            send_email(email_or_phone, code)
        elif check_email_or_phone(email_or_phone) == 'email':
            code = user.create_verify_code(VIA_EMAIL)
            send_email(email_or_phone, code)
        return Response(
            {
                'success': True,
                'message': 'Your confirmation code sent again!',
                'access': user.token()['access'],
                'refresh': user.token()['refresh_token'],
                'user_status': user.auth_status,
            }, status=status.HTTP_200_OK
        )


class ResetPasswordApiView(UpdateAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [IsAuthenticated, ]
    http_method_names = ['put', 'patch', ]

    def get_object(self):
        return self.request.user  # qaysi user passwordini o'zgartirish

    def update(self, request, *args, **kwargs):
        response = super(ResetPasswordApiView, self).update(request, *args, **kwargs)
        try:
            user = User.objects.get(id=response.data.get('id'))
        except ObjectDoesNotExist:
            raise NotFound(detail='User not found')
        data = {'success': True,
                'message': 'Password reset successfully',
                'access': user.token()['access'],
                'refresh': user.token()['refresh_token'], }
        return Response(data, status=status.HTTP_200_OK)
