from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

INDEX_PAGE = reverse('posts:index')
GROUP_SLUG = 'test_slug'
GROUP_POSTS = reverse('posts:group_list', args=[GROUP_SLUG])
AUTHOR_NAME = 'TestUser'
AUTHOR_POSTS = reverse('posts:profile', args=[AUTHOR_NAME])
POST_ID = '1'
POST_PAGE = reverse('posts:post_detail', args=[POST_ID])
POST_CREATE_PAGE = reverse('posts:post_create')
POST_EDIT_PAGE = reverse('posts:post_edit', args=[POST_ID])


class StaticURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Название тестовой группы',
            slug='test_slug',
            description='Описание тестовой группы',
        )
        cls.author = User.objects.create(username='TestUser')
        cls.scnd_author = User.objects.create(username='ScndTestUser')
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст',
        )
        cls.scnd_user_post = Post.objects.create(
            author=cls.scnd_author,
            text='Тестовый текст второго пользователя'
        )

    def setUp(self):
        self.guest_client = Client()
        self.main_author_client = Client()
        self.main_author_client.force_login(self.author)
        self.scnd_author_client = Client()
        self.scnd_author_client.force_login(self.scnd_author)

    def test_pages_unuthorized_users(self):
        """Страницы posts доступные неавторизованным пользователям."""
        url_list = {
            INDEX_PAGE: 'Главная страница',
            GROUP_POSTS: 'Страница групп',
            AUTHOR_POSTS: 'Посты пользователя',
            POST_PAGE: 'Страница поста',
        }
        for url, url_names in url_list.items():
            with self.subTest(url_names=url_names):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_redirect_unuthorized_users(self):
        """Страницы posts не доступные неавторизованным пользователям."""
        url_list = {
            POST_CREATE_PAGE: '/auth/login/?next=/create/',
            POST_EDIT_PAGE: f'/auth/login/?next=/posts/{self.post.pk}/edit/',
        }
        for url, url_names in url_list.items():
            with self.subTest(url_names=url_names):
                response = self.guest_client.get(url)
                self.assertRedirects(response, url_names)
                # Несуществующая страница
                response = self.guest_client.get('/unexpected-page/')
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_pages_author(self):
        """Страницы posts доступные автору."""
        url_list = {
            INDEX_PAGE: 'Главная страница',
            GROUP_POSTS: 'Страница групп',
            AUTHOR_POSTS: 'Посты пользователя',
            POST_PAGE: 'Страница поста',
            POST_CREATE_PAGE: 'Создание поста',
            POST_EDIT_PAGE: 'Редактированиe поста',
        }
        for url, url_names in url_list.items():
            with self.subTest(url_names=url_names):
                response = self.main_author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_redirects_non_author(self):
        """Страницы posts не доступные автору."""
        # Страница редактирования чужого поста
        response = self.main_author_client.get('/posts/2/edit/')
        self.assertRedirects(response, '/posts/2/')
        # Несуществующая страница
        response = self.main_author_client.get('/unexpected-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_templates(self):
        """Страницы posts соответствуют шаблонам."""
        templates_urls = {
            'posts/index.html': INDEX_PAGE,
            'posts/group_list.html': GROUP_POSTS,
            'posts/post_detail.html': POST_PAGE,
            'posts/create_post.html': POST_CREATE_PAGE,
            'posts/profile.html': AUTHOR_POSTS,
        }
        for template, url in templates_urls.items():
            with self.subTest(url=url):
                response = self.main_author_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_index_cache(self):
        """Кэширование главной страницы."""
        post_count = Post.objects.count()
        self.main_author_client.delete(POST_PAGE)
        self.assertEqual(Post.objects.count(), post_count)
