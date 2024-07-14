from django.urls import path
from .views import (PostListApiView, PostCreateApiView, PostRetrieveUpdateDestroyApiView, PostCommentListApiView,
                    PostCommentCreateApiView, CommentListCreateApiView, )

urlpatterns = [
    path('list/', PostListApiView.as_view()),
    path('create/', PostCreateApiView.as_view()),
    path('<uuid:pk>/', PostRetrieveUpdateDestroyApiView.as_view()),
    path('<uuid:pk>/comments/', PostCommentListApiView.as_view()),
    path('<uuid:pk>/comments/create/', PostCommentCreateApiView.as_view()),
    path('comments/', CommentListCreateApiView.as_view()),

]
