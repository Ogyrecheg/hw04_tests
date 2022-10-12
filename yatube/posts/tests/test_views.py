from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..constants import INDEX_PER_PAGE_LIMIT
from ..forms import PostForm
from ..models import Post, Group

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
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
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.user)

    def test_pages_uses_correct_template(self):
        pages_names_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'test_user'}):
                'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={
                    'post_id': f'{PostPagesTests.post.id}',
                }): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': f'{PostPagesTests.post.id}'}):
                'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }

        for reverse_name, template in pages_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)


class TestPostContext(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        Post.objects.bulk_create(
            [Post(
                author=cls.user,
                group=cls.group,
                text=f'Тестовый пост № {i}',
            )for i in range(13)]
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(TestPostContext.user)

    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        expected_list = list(Post.objects.all()[:INDEX_PER_PAGE_LIMIT])
        context_list = response.context.get('page_obj').object_list
        self.assertListEqual(context_list, expected_list)

    def test_group_list_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': 'test_slug'}))
        expected_list = list(
            TestPostContext.group.posts.all()[:INDEX_PER_PAGE_LIMIT])
        context_list = response.context.get('page_obj').object_list
        self.assertListEqual(context_list, expected_list)

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': 'test_user'}))
        expected_list = list(
            TestPostContext.user.posts.all()[:INDEX_PER_PAGE_LIMIT])
        context_list = response.context.get('page_obj').object_list
        self.assertListEqual(context_list, expected_list)

    def test_post_detail_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': 1}))
        expected_post = Post.objects.get(id=1)
        context_post = response.context.get('post')
        self.assertEqual(context_post, expected_post)

    def test_post_create_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        expected_form = type(PostForm())
        context_form = type(response.context.get('form'))
        self.assertEqual(context_form, expected_form)

    def test_post_edit_form_show_correct_context(self):
        """Честно, хз как проверить форму редактирования поста"""

        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': 1}))
        expected_form = type(PostForm())
        context_form = type(response.context.get('form'))
        self.assertEqual(context_form, expected_form)

    def test_first_paginator_page_contains_ten_records(self):
        pages_name_paginator_records = {
            reverse('posts:index'): 10,
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}): 10,
            reverse('posts:profile', kwargs={'username': 'test_user'}): 10,
        }
        for reverse_name, pag_records in pages_name_paginator_records.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']), pag_records)

    def test_second_paginator_page_contains_three_records(self):
        pages_name_paginator_records = {
            reverse('posts:index'): 3,
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}): 3,
            reverse('posts:profile', kwargs={'username': 'test_user'}): 3,
        }
        for reverse_name, pag_records in pages_name_paginator_records.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']), pag_records)


class TestOnePost(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group_one = Group.objects.create(
            title='Тестовая группа 1',
            slug='test_slug_one',
            description='Тестовое описание 1',
        )
        cls.group_two = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_slug_two',
            description='Тестовое описание 2',
        )
        Post.objects.bulk_create(
            [Post(
                author=cls.user,
                group=cls.group_one,
                text=f'Тестовый пост № {i}',
            ) for i in range(5)]
        )
        Post.objects.create(
            author=cls.user,
            group=cls.group_two,
            text='Новый тестовый пост',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(TestOnePost.user)

    def test_pages_show_correct_count_posts(self):
        pages_posts_count = {
            reverse('posts:index'): 6,
            reverse('posts:group_list', kwargs={'slug': 'test_slug_one'}): 5,
            reverse('posts:profile', kwargs={'username': 'test_user'}): 6,
        }
        for page, posts_count in pages_posts_count.items():
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertEqual(
                    len(
                        response.context.get('page_obj').object_list
                    ), posts_count)
