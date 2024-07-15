from django.urls import path
from .views import (PostListApiView, PostCreateApiView, PostRetrieveUpdateDestroyApiView, PostCommentListApiView,
                    PostCommentCreateApiView, CommentListCreateApiView, PostLikeListApiView, CommentLikeListApiView,
                    CommentRetrieveApiView, PostLikeApiView, CommentLikeApiView)

urlpatterns = [
    path('list/', PostListApiView.as_view()),
    path('create/', PostCreateApiView.as_view()),
    path('<uuid:pk>/', PostRetrieveUpdateDestroyApiView.as_view()),
    path('<uuid:pk>/likes/create-delete/', PostLikeApiView.as_view()),
    path('<uuid:pk>/comments/', PostCommentListApiView.as_view()),
    path('<uuid:pk>/comments/create/', PostCommentCreateApiView.as_view()),
    path('comments/', CommentListCreateApiView.as_view()),
    path('<uuid:pk>/likes/', PostLikeListApiView.as_view()),
    path('comments/<uuid:pk>/likes/', CommentLikeListApiView.as_view()),
    path('comments/<uuid:pk>/', CommentRetrieveApiView.as_view()),
    path('comments/<uuid:pk>/likes/create-delete/', CommentLikeApiView.as_view())
]
