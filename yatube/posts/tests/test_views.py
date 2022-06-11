
from django import forms
from django.core.paginator import Paginator
from django.test import Client, TestCase
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
        post_obj = [Post(
            text='Тестовый текст',
            group=cls.group,
            author=cls.author,
            pk='%s' % i
        ) for i in range(12)]
        cls.posts = Post.objects.bulk_create(post_obj)

        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст',
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            author=cls.author,
            text='Тестовый коммент',
            post=cls.post,
        )
        cls.paginator = Paginator(Post.objects.all(), POSTS_ON_PAGE)

    def setUp(self):
        self.guest_client = Client()
        self.author_following = Client()
        self.author_following.force_login(self.author)
        self.non_author_follower = Client()
        self.non_author_follower.force_login(self.non_author)

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
                response = self.author_following.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_edit_correct_template_non_author(self):
        """Использование ложным автором posts view ожидаемых шаблонов."""
        template_pages = {'posts/create_post.html':
                          POST_EDIT_PAGE,
                          }
        for template, reverse_name in template_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.non_author_follower.get(reverse_name)
                self.assertTemplateNotUsed(response, template)

    def test_create_show_correct_context(self):
        """Проверка форм страницы создания поста."""
        response = self.author_following.get(POST_CREATE_PAGE)
        form_field = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_field.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_show_correct_context(self):
        """Проверка форм страницы редактирования поста."""
        response = self.author_following.get(
            POST_EDIT_PAGE)
        form_field = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
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
        }
        for obj, context in page_obj.items():
            with self.subTest(context=context):
                self.assertEqual(obj, context)

    def test_group_list_show_correct_context(self):
        """Проверка контекста страницы постов групп."""
        response = self.guest_client.get(GROUP_POSTS)
        group = response.context['group']
        page_obj = {
            self.post.text: self.first_object(response).text,
            self.post.author: self.first_object(response).author,
            self.post.group: group,
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
        response = self.author_following.get(AUTHOR_POSTS)
        author = response.context['author']
        context_counter = response.context['count']
        page_obj = {
            self.post.text: self.first_object(response).text,
            self.post.group: self.first_object(response).group,
            self.post.author: author,
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
        response = self.author_following.get(POST_PAGE)
        form_field = {
            'text': forms.fields.CharField,
        }
        for value, expected in form_field.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_subscription_available_authorize(self):
        """Доступность возможности подписаться и отписаться."""
        response = self.non_author_follower.get(AUTHOR_POSTS)
        self.assertEqual(
            response.context['following'], True)

    def test_follow_index_context(self):
        """Появление нового поста для подписчиков."""
        response = self.non_author_follower.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(self.first_object(response).author,
                         self.author)
