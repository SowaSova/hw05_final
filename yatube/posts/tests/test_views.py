import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.paginator import Paginator
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from yatube.settings import POSTS_ON_PAGE

from ..models import Comment, Follow, Group, Post, User

INDEX_PAGE = reverse('posts:index')
GROUP_SLUG = 'test_slug'
GROUP_POSTS = reverse('posts:group_list', args=[GROUP_SLUG])
AUTHOR_NAME = 'TestUser'
AUTHOR_POSTS = reverse('posts:profile', args=[AUTHOR_NAME])
POST_ID = '1'
POST_PAGE = reverse('posts:post_detail', args=[POST_ID])
POST_CREATE_PAGE = reverse('posts:post_create')
POST_EDIT_PAGE = reverse('posts:post_edit', args=[POST_ID])
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='TestUser')
        cls.non_author = User.objects.create_user(username='non_author')
        cls.group = Group.objects.create(
            title='Тест группа',
            slug='test_slug',
            description='Описание',
        )
        cls.scnd_group = Group.objects.create(
            title='Вторая тест группа',
            slug='scnd_test_slug',
            description='Описание второй',
        )
        cls.follower = Follow.objects.create(
            author=cls.author,
            user=cls.non_author
        )
        cls.image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='smallVIEWS.png',
            content=cls.image,
            content_type='image/png'
        )

        post_obj = [Post(
            text='Тестовый текст',
            group=cls.group,
            author=cls.author,
            image=cls.uploaded,
            pk='%s' % i
        ) for i in range(12)]
        cls.posts = Post.objects.bulk_create(post_obj)

        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст',
            group=cls.group,
            image=cls.uploaded,
        )
        cls.comment = Comment.objects.create(
            author=cls.author,
            text='Тестовый коммент',
            post=cls.post,
        )
        cls.paginator = Paginator(Post.objects.all(), POSTS_ON_PAGE)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.non_author_client = Client()
        self.non_author_client.force_login(self.non_author)

    def test_pages_uses_correct_template_authorized(self):
        """Использование автором posts view ожидаемых шаблонов."""
        template_pages = {
            'posts/index.html': INDEX_PAGE,
            'posts/group_list.html': GROUP_POSTS,
            'posts/post_detail.html': POST_PAGE,
            'posts/profile.html': AUTHOR_POSTS,
            'posts/create_post.html': POST_CREATE_PAGE,
        }
        for template, reverse_name in template_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_edit_correct_template_non_author(self):
        """Использование ложным автором posts view ожидаемых шаблонов."""
        template_pages = {'posts/create_post.html':
                          POST_EDIT_PAGE,
                          }
        for template, reverse_name in template_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.non_author_client.get(reverse_name)
                self.assertTemplateNotUsed(response, template)

    def test_create_show_correct_context(self):
        """Проверка форм страницы создания поста."""
        response = self.author_client.get(POST_CREATE_PAGE)
        form_field = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_field.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_show_correct_context(self):
        """Проверка форм страницы редактирования поста."""
        response = self.author_client.get(
            POST_EDIT_PAGE)
        form_field = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_field.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def first_object(self, response):
        """Первый объект из контекста posts views."""
        return response.context['page_obj'][0]

    def test_index_show_correct_context(self):
        """Проверка контекста главной страницы."""
        response = self.guest_client.get(INDEX_PAGE)
        page_obj = {
            self.post.text: self.first_object(response).text,
            self.post.author: self.first_object(response).author,
            self.post.group: self.first_object(response).group,
            self.post.image: self.first_object(response).image,
        }
        for obj, context in page_obj.items():
            with self.subTest(context=context):
                self.assertEqual(obj, context)

    def test_group_list_show_correct_context(self):
        """Проверка контекста страницы постов групп."""
        response = self.author_client.get(GROUP_POSTS)
        group = response.context['group']
        page_obj = {
            self.post.text: self.first_object(response).text,
            self.post.author: self.first_object(response).author,
            self.post.group: group,
            self.post.image: self.first_object(response).image,
        }
        for obj, context in page_obj.items():
            with self.subTest(context=context):
                self.assertEqual(obj, context)

    def test_wrong_group_list_show_correct_context(self):
        """Проверка отсутствия поста на странице чужой группы."""
        response = self.guest_client.get(GROUP_POSTS)
        group = response.context['group']
        self.assertNotEqual(group, self.scnd_group)

    def test_profile_list_show_correct_context(self):
        """Проверка контекста страницы постов автора."""
        response = self.author_client.get(AUTHOR_POSTS)
        author = response.context['author']
        context_counter = response.context['count']
        page_obj = {
            self.post.text: self.first_object(response).text,
            self.post.group: self.first_object(response).group,
            self.post.author: author,
            self.post.image: self.first_object(response).image,
            Post.objects.filter(author=self.author).count(): context_counter,
        }
        for obj, context in page_obj.items():
            with self.subTest(context=context):
                self.assertEqual(obj, context)

    def test_detail_show_correct_context(self):
        """Проверка контекста страницы поста."""
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        post_obj = response.context['post']
        author = response.context['author']
        context_counter = response.context['post_count']
        comments = response.context['comments'][0]
        page_obj = {
            self.post.text: post_obj.text,
            self.post.author: author,
            self.post.image: post_obj.image,
            self.comment: comments,
            Post.objects.filter(author=self.author).count(): context_counter,
        }
        for obj, context in page_obj.items():
            with self.subTest(context=context):
                self.assertEqual(obj, context)

    def test_first_page_contains_ten_records(self):
        """Первая страница пагинатора -- 10 постов."""
        url_list = {
            INDEX_PAGE,
            GROUP_POSTS,
            AUTHOR_POSTS,
        }
        for url in url_list:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertCountEqual(
                    response.context['page_obj'], POSTS_ON_PAGE)

    def test_first_page_contains_ten_records(self):
        """Вторая страница пагинатора оставшиеся посты."""
        url_list = {
            INDEX_PAGE + '?page=2',
            GROUP_POSTS + '?page=2',
            AUTHOR_POSTS + '?page=2',
        }
        for url in url_list:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    len(response.context['page_obj']),
                    self.paginator.count % POSTS_ON_PAGE)

    def test_comment_only_authorized(self):
        """Проверка создания комментария."""
        response = self.author_client.get(POST_PAGE)
        form_field = {
            'text': forms.fields.CharField,
        }
        for value, expected in form_field.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_index_cache(self):
        """Кэширование главной страницы."""
        post_count = Post.objects.count()
        self.author_client.delete(POST_PAGE)
        self.assertEqual(Post.objects.count(), post_count)


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.user = User.objects.create_user(username='non_author')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author,
        )
        cls.following = Client()
        cls.following.force_login(cls.author)
        cls.follower = Client()
        cls.follower.force_login(cls.user)

    def test_subscription_available_authorize(self):
        """Доступность возможности подписаться."""
        counter = Follow.objects.filter(
            author=self.author, user=self.user).count()
        self.follower.get(
            reverse('posts:profile_follow', args=[self.author]))
        self.assertEqual(Follow.objects.count(), counter + 1)

    def test_unsub_available(self):
        """Доступность отписки."""
        counter = Follow.objects.filter(
            author=self.author, user=self.user).count()
        self.follower.get(
            reverse('posts:profile_follow', args=[self.author]))
        self.follower.get(
            reverse('posts:profile_unfollow', args=[self.author]))
        self.assertEqual(Follow.objects.count(), counter)

    def test_double_following(self):
        """Нельзя подписаться повторно."""
        counter = Follow.objects.filter(
            author=self.author, user=self.user).count()
        self.follower.get(
            reverse('posts:profile_follow', args=[self.author]))
        self.follower.get(
            reverse('posts:profile_follow', args=[self.author]))
        self.assertEqual(Follow.objects.count(), counter + 1)

    def test_self_follow(self):
        counter = Follow.objects.filter(
            author=self.author, user=self.user).count()
        self.follower.get(
            reverse('posts:profile_follow', args=[self.user]))
        self.assertEqual(Follow.objects.count(), counter)

    def test_post_follow_page(self):
        """ПОст на странице подписчика."""
        Follow.objects.create(user=self.user, author=self.author)
        response = self.follower.get(reverse('posts:follow_index'))
        self.assertIn(self.post, response.context['page_obj'])
