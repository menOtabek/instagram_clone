from django.urls import path
from .views import PostListApiView, CreatePostApiView, PostRetrieveUpdateDestroyApiView
urlpatterns = [
    path('posts/', PostListApiView.as_view()),
    path('posts/create/', CreatePostApiView.as_view()),
    path('posts/<uuid:pk>/', PostRetrieveUpdateDestroyApiView.as_view()),

]