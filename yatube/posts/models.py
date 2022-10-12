from django.contrib.auth import get_user_model
from django.db import models

from .constants import POST_STR_LIM

User = get_user_model()


class Post(models.Model):
    """Модель постов."""

    text = models.TextField(verbose_name='текст поста')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='автор поста',
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='группа постов',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        """Метод, позволяющий получить text объекта"""
        return self.text[:POST_STR_LIM]


class Group(models.Model):
    """Модель групп постов."""

    title = models.CharField(max_length=200, verbose_name='заголовок группы')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='слаг')
    description = models.TextField(verbose_name='описание группы')

    def __str__(self):
        """Метод, позволяющий получить title объекта Group."""
        return self.title
