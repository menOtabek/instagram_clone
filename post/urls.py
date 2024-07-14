from django.urls import path
from .views import PostListApiView
urlpatterns = [
    path('post-list', PostListApiView.as_view()),
]