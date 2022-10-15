from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.group_two = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_slug_two',
            description='Тестовое описание второй группы'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.user)

    def test_create_post_page_add_new_row_in_db(self):
        """Тестируем форму, добавляющую новую запись в базу."""

        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост добавлен из формы',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
        )
        first_post = Post.objects.first()
        self.assertRedirects(response,
                             reverse('posts:profile',
                                     kwargs={'username': 'test_user'}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(first_post.group, self.group)
        self.assertEqual(first_post.text, form_data['text'])
        self.assertEqual(first_post.author, self.user)

    def test_post_edit_page_make_change_in_post(self):
        """Тестируем форму, изменяющую данные поста."""

        posts_count = Post.objects.count()
        form_data = {
            'text': 'Измененный тестовый пост',
            'group': self.group_two.id,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id}))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(Post.objects.get(id=1).text, form_data['text'])
        self.assertEqual(
            Post.objects.get(id=1).group.title,
            self.group_two.title
        )
