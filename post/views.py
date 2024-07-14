from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Post, PostLike, PostComment, CommentLike
from .serializers import PostSerializer, PostLikeSerializer, CommentSerializer, CommentLikeSerializer
from shared.custom_pagination import CustomPagination


class PostListApiView(generics.ListAPIView):
    permission_classes = [AllowAny, ]
    serializer_class = PostSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return Post.objects.all()

