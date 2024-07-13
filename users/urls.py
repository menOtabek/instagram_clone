from django.urls import path
# from .serializers import SignUpSerializer
from .views import (CreateUserView, VerifyAPIView, NewVerifyCodeAPIView,
                    ChangeUserInformationView, ChangeUserPhotoView, LoginView, LoginRefreshView, LogoutView,
                    ForgotPasswordAPIView, ResetPasswordApiView)

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('login/refresh/', LoginRefreshView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('signup/', CreateUserView.as_view()),
    path('verify-code/', VerifyAPIView.as_view()),
    path('new-verify-code/', NewVerifyCodeAPIView.as_view()),
    path('change-user-information/', ChangeUserInformationView.as_view()),
    path('change-user-photo/', ChangeUserPhotoView.as_view()),
    path('forgot-password/', ForgotPasswordAPIView.as_view()),
    path('reset-password/', ResetPasswordApiView.as_view()),
]
