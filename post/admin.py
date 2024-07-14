from django.contrib import admin
from .models import Post, PostLike, PostComment, CommentLike


class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'caption', 'author', 'created_at', )
    list_display_links = ('id', 'author', )
    search_fields = ('id', 'caption', 'author__username', )


class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'post', 'created_at', )
    list_display_links = ('id', 'author', )
    search_fields = ('id', 'author__username', )


class PostCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'post', 'created_at', )
    list_display_links = ('id', 'author', )
    search_fields = ('id', 'author__username', )


class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'comment', 'created_at', )
    list_display_links = ('id', 'author', )
    search_fields = ('id', 'author__username', )


admin.site.register(Post, PostAdmin)
admin.site.register(PostLike, PostLikeAdmin)
admin.site.register(PostComment, PostCommentAdmin)
admin.site.register(CommentLike, CommentLikeAdmin)
