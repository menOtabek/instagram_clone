from django.urls import path
from .views import (PostListApiView, PostCreateApiView, PostRetrieveUpdateDestroyApiView, PostCommentListApiView,
                    PostCommentCreateApiView, )

urlpatterns = [
    path('posts/', PostListApiView.as_view()),
    path('posts/create/', PostCreateApiView.as_view()),
    path('posts/<uuid:pk>/', PostRetrieveUpdateDestroyApiView.as_view()),
    path('posts/<uuid:pk>/comments/', PostCommentListApiView.as_view()),
    path('posts/<uuid:pk>/comments/create/', PostCommentCreateApiView.as_view()),

]
