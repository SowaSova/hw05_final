from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UsersURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user("john", "len@non.ru", "lennon")

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_users_pages_all_users(self):
        """Страницы users доступные неавторизованным пользователям."""
        url_list = {
            "/auth/signup/": HTTPStatus.OK,
            "/auth/login/": HTTPStatus.OK,
            "/auth/logout/": HTTPStatus.OK,
            "/auth/password_reset/": HTTPStatus.OK,
            "/auth/password_reset/done/": HTTPStatus.OK,
            "/auth/reset/uidb64/token/": HTTPStatus.OK,
            "/auth/reset/done/": HTTPStatus.OK,
        }
        for url, result in url_list.items():
            with self.subTest(result=result):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, result)

    def test_users_pages_authorized(self):
        """Страницы users доступные авторизованным пользователям."""
        url_list = {
            "/auth/password_change/": HTTPStatus.OK,
            "/auth/password_change/done/": HTTPStatus.OK,
        }
        for url, result in url_list.items():
            with self.subTest(result=result):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, result)

    def test_users_pages_uses_correct_templates_all(self):
        """Страницы users соответствуют шаблонам."""
        template_url = {
            "/auth/signup/": "users/signup.html",
            "/auth/login/": "users/login.html",
            "/auth/logout/": "users/logged_out.html",
            "/auth/password_reset/": "users/password_reset_form.html",
            "/auth/password_reset/done/": "users/password_reset_done.html",
            "/auth/reset/uidb64/token/": "users/password_reset_confirm.html",
            "/auth/reset/done/": "users/password_reset_complete.html",
        }
        for url, template in template_url.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_users_pages_uses_correct_templates_authorized(self):
        """Страницы авторизованных users соответствуют шаблонам."""
        template_url = {
            "/auth/password_change/": "users/password_change_form.html",
            "/auth/password_change/done/": "users/password_change_done.html",
        }
        for url, template in template_url.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
