from django.contrib.auth import get_user_model
from django.test import TestCase

from ..constants import POST_STR_LIM
from ..models import Post, Group


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        group = PostModelTest.group
        group_expected_object_name = group.title
        self.assertEqual(group_expected_object_name, str(group))

        post = PostModelTest.post
        post_expected_object_name = post.text[:POST_STR_LIM]
        self.assertEqual(post_expected_object_name, str(post))
