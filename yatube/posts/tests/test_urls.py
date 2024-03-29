from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.not_author = User.objects.create_user(username='not_author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)
        self.authorized_not_author_client = Client()
        self.authorized_not_author_client.force_login(PostURLTests.not_author)

    def test_public_urls_exists_desired_location(self):
        """
        Тестируем доступность и работоспособность станиц
        для всех пользователей.
        """

        public_urls_response_code = {
            '/': HTTPStatus.OK,
            f'/group/{PostURLTests.group.slug}/': HTTPStatus.OK,
            f'/profile/{PostURLTests.user.username}/': HTTPStatus.OK,
            f'/posts/{PostURLTests.post.id}/': HTTPStatus.OK,
            '/unexistings_page/': HTTPStatus.NOT_FOUND,
        }

        for url, response_code in public_urls_response_code.items():
            with self.subTest(url=url):
                response_guest = self.guest_client.get(url)
                self.assertEqual(response_guest.status_code, response_code)
                response_user = self.authorized_client.get(url)
                self.assertEqual(response_user.status_code, response_code)

    def test_create_url_exists_desired_location(self):
        """
        Тестируем доступность и работоспособность страницы
         /create/ для авторизованного пользователя.
        """

        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_exists_desired_location_for(self):
        """
        Тестируем доступность и работоспосбность для/posts/<post_id>/edit/
        для гостей и зареганного неавтора поста.
        """

        response_guest = self.guest_client.get(
            f'/posts/{PostURLTests.post.id}/edit/')
        self.assertRedirects(
            response_guest,
            f'/auth/login/?next=/posts/{PostURLTests.post.id}/edit/'
        )

        response_not_author = self.authorized_not_author_client.get(
            f'/posts/{PostURLTests.post.id}/edit/')
        self.assertRedirects(
            response_not_author, f'/posts/{PostURLTests.post.id}/')

    def test_urls_uses_correct_template(self):
        """Тестируем корректность отображения шаблонов для urls."""

        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{PostURLTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{PostURLTests.user.username}/': 'posts/profile.html',
            f'/posts/{PostURLTests.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{PostURLTests.post.id}/edit/': 'posts/create_post.html',
        }

        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
