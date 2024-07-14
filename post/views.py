from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import Post, PostLike, PostComment, CommentLike
from .serializers import PostSerializer, PostLikeSerializer, CommentSerializer, CommentLikeSerializer
from shared.custom_pagination import CustomPagination


class PostListApiView(generics.ListAPIView):
    permission_classes = [AllowAny, ]
    serializer_class = PostSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return Post.objects.all()


class PostCreateApiView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostRetrieveUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    def put(self, request, *args, **kwargs):
        post = self.get_object()
        serializer = self.serializer_class(post, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                'success': True,
                'data': serializer.data,
                'message': 'Post successfully updated',
            }, status=status.HTTP_200_OK
        )

    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        post.delete()
        return Response(
            {
                'success': True,
                'message': 'Post successfully deleted',
            }, status=status.HTTP_204_NO_CONTENT
        )


class PostCommentListApiView(generics.ListAPIView):
    permission_classes = [AllowAny, ]
    serializer_class = CommentSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        post_id = self.kwargs['pk']
        queryset = PostComment.objects.filter(post__id=post_id)
        return queryset


class PostCommentCreateApiView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        post_id = self.kwargs['pk']
        serializer.save(author=self.request.user, post_id=post_id)


class CommentListCreateApiView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = CommentSerializer
    pagination_class = CustomPagination
    queryset = Post.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentRetrieveApiView(generics.RetrieveAPIView):
    permission_classes = [AllowAny, ]
    serializer_class = CommentSerializer
    queryset = PostComment.objects.all()


class PostLikeListApiView(generics.ListAPIView):
    permission_classes = [AllowAny, ]
    serializer_class = PostLikeSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        post_id = self.kwargs['pk']
        queryset = PostLike.objects.filter(post_id=post_id)
        return queryset


class CommentLikeListApiView(generics.ListAPIView):
    permission_classes = [AllowAny, ]
    serializer_class = CommentLikeSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        comment_id = self.kwargs['pk']
        queryset = CommentLike.objects.filter(comment_id=comment_id)
        return queryset
