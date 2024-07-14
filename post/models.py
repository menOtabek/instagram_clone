from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator, MaxLengthValidator
from django.db import models
from django.db.models import UniqueConstraint

from shared.models import BaseModel

User = get_user_model()


class Post(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(upload_to='post_images/',
                              validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])])
    caption = models.TextField(validators=[MaxLengthValidator(2000)])

    class Meta:
        db_table = 'posts'
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    def __str__(self):
        return f"{self.author}'s post about {self.caption}"


class PostComment(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, related_name='child', on_delete=models.CASCADE)

    def __str__(self):
        return f"Comment by {self.author}"


class PostLike(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['author', 'post'],
                name='PostLikeUnique'
            )
        ]


class CommentLike(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['author', 'comment'],
                name='CommentLikeUnique'
            )
        ]
