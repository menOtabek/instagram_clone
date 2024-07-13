from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from django.core.validators import FileExtensionValidator
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken

from .models import User, UserConfirmation, VIA_EMAIL, VIA_PHONE, NEW, CODE_VERIFIED, DONE, PHOTO_STEP
from rest_framework import serializers, exceptions
from django.db.models import Q
from rest_framework.exceptions import ValidationError, PermissionDenied
from shared.utility import check_email_or_phone, send_email, send_phone_code, check_user_type


class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    # modelga bog'liq bo'lmagan holda yangi field qo'shamiz __init__ orqali
    def __init__(self, *args, **kwargs):
        super(SignUpSerializer, self).__init__(*args, **kwargs)
        self.fields['email_phone_number'] = serializers.CharField(required=False)

    # auth_type = serializers.CharField(read_only=True, required=False)    # extrakwargsdagi bilan teng kuchli
    # aut_status = serializers.CharField(read_only=True, required=False)   # extrakwargsdagi bilan teng kuchli
    class Meta:
        model = User
        fields = (
            'id',
            'auth_types',
            'auth_status',
        )

        extra_kwargs = {
            'auth_types': {'read_only': True, 'required': False},
            'auth_status': {'read_only': True, 'required': False}
        }

    def create(self, validated_data):
        user = super(SignUpSerializer, self).create(validated_data)
        if user.auth_types == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            send_email(user.email, code)
        elif user.auth_types == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            send_email(user.phone_number, code)
            # send_phone_code(user.phone_number, code)
        user.save()
        return user

    def validate(self, data):
        super(SignUpSerializer, self).validate(data)
        data = self.auth_validate(data)
        return data

    @staticmethod
    def auth_validate(data):
        user_input = str(data.get('email_phone_number')).lower()
        input_type = check_email_or_phone(user_input)
        if input_type == 'email':
            data = {
                'email': user_input,
                'auth_types': VIA_EMAIL
            }
        elif input_type == 'phone':
            data = {
                'phone_number': user_input,
                'auth_types': VIA_PHONE
            }
        else:
            data = {
                'success': False,
                'message': 'You should send valid email or phone number'
            }
            raise ValidationError(data)

        return data

    @staticmethod
    def validate_email_phone_number(value):
        value = value.lower()
        if value and User.objects.filter(email=value).exists():
            data = {
                'success': False,
                'message': 'Email already exists'
            }
            raise ValidationError(data)
        elif value and User.objects.filter(phone_number=value).exists():
            data = {
                'success': False,
                'message': 'Phone number already exists'
            }
            raise ValidationError(data)
        return value

    def to_representation(self, instance):
        data = super(SignUpSerializer, self).to_representation(instance)
        data.update(instance.token())

        return data


class ChangeUserInformation(serializers.Serializer):
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        password = data.get('password', None)
        confirm_password = data.get('confirm_password', None)
        if password != confirm_password:
            data = {'success': False, 'message': 'Passwords do not match'}
            raise ValidationError(data)
        if password and confirm_password:
            validate_password(password)
            validate_password(confirm_password)
        return data

    @staticmethod
    def validate_username(self, username):
        if len(username) < 3 or len(username) > 64:
            data = {'success': False, 'message': 'Username must be between 3 and 64 characters'}
            raise ValidationError(data)
        if not username.isalpha:
            data = {'success': False, 'message': 'Username can not be entirely numeric'}
            raise ValidationError(data)
        return username

    @staticmethod
    def validate_first_name(self, first_name):
        if len(first_name) < 3 or len(first_name) > 64:
            data = {'success': False, 'message': 'First name must be between 3 and 64 characters'}
            raise ValidationError(data)
        if not first_name.isalpha():
            data = {'success': False, 'message': 'First name must contain only alphabetic characters'}
            raise ValidationError(data)
        return first_name

    @staticmethod
    def validate_last_name(self, last_name):
        if len(last_name) < 3 or len(last_name) > 64:
            data = {'success': False, 'message': 'Last name must be between 3 and 64 characters'}
            raise ValidationError(data)
        if not last_name.isalpha():
            data = {'success': False, 'message': 'Last name must contain only alphabetic characters'}
            raise ValidationError(data)
        return last_name

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.username = validated_data.get('username', instance.username)
        instance.password = validated_data.get('password', instance.password)
        if validated_data.get('password'):
            instance.set_password(validated_data.get('password'))
        if instance.auth_status == CODE_VERIFIED:
            instance.auth_status = DONE
        instance.save()
        return instance


class ChangeUserPhotoSerializer(serializers.Serializer):
    photo = serializers.ImageField(validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])])

    def update(self, instance, validated_data):
        photo = validated_data.get('photo')
        if photo:
            instance.photo = photo
            instance.auth_status = PHOTO_STEP
            instance.save()
        return instance


class LoginSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super(LoginSerializer, self).__init__(*args, **kwargs)
        self.fields['user_input'] = serializers.CharField(required=True)
        self.fields['username'] = serializers.CharField(read_only=True, required=False)

    def auth_validate(self, data):
        user_input = str(data.get('user_input')).lower()
        if check_user_type(user_input) == 'username':
            username = user_input
        elif check_user_type(user_input) == 'email':
            user = self.get_user(email__iexact=user_input)
            username = user.username
        elif check_user_type(user_input) == 'phone':
            user = self.get_user(phone_number=user_input)
            username = user.username
        else:
            data = {'success': False, 'message': 'You should send valid email or phone number or username'}
            raise ValidationError(data)
        authentication_kwargs = {
            self.username_field: username,
            'password': data.get('password')
        }
        current_user = User.objects.filter(username__iexact=username).first()
        if current_user is not None and current_user.auth_status in [CODE_VERIFIED, NEW]:
            data = {
                'success': False,
                'message': 'You did not fully registered yet'
            }
            raise ValidationError(data)
        user = authenticate(**authentication_kwargs)

        if user is not None:
            self.user = user
        else:
            data = {'success': False, 'message': 'Login or password is incorrect, please try again'}
            raise ValidationError(data)

    def validate(self, data):
        self.auth_validate(data)
        if self.user.auth_status not in [DONE, PHOTO_STEP]:
            data = {
                'success': False,
                'message': 'You have not permission to login'
            }
            raise PermissionDenied(data)
        data = self.user.token()
        data['auth_status'] = self.user.auth_status
        return data

    @staticmethod
    def get_user(**kwargs):
        users = User.objects.filter(**kwargs)
        if not users.exists():
            data = {'success': False, 'message': 'User not found'}
            raise ValidationError(data)
        return users.first()


class LoginRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        access_token_instance = AccessToken(data['access'])
        user_id = access_token_instance['user_id']
        user = get_object_or_404(User, id=user_id)
        update_last_login(None, user)
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        email_or_phone = attrs.get('email_or_phone')
        if not email_or_phone:
            data = {'success': False, 'message': 'Email or phone number required'}
            raise ValidationError(data)
        user = User.objects.filter(Q(email=email_or_phone) | Q(phone_number=email_or_phone))
        if not user:
            data = {'success': False, 'message': 'User not found'}
            raise ValidationError(data)
        attrs['user'] = user.first()
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = User
        fields = ('id', 'password', 'confirm_password')

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        if password != confirm_password:
            data = {'success': False, 'message': 'Passwords do not match'}
            raise ValidationError(data)
        if password:
            validate_password(password)
            return data

    def update(self, instance, validated_data):
        password = validated_data.pop('password')
        instance.set_password(password)
        instance.save()
        return instance
        # return super(ResetPasswordSerializer, self).update(instance, validated_data)  # password update qilinyapti
