import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CoreTestClass(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_count = Post.objects.count()
        image = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        cls.uploaded = SimpleUploadedFile(
            name="image.png", content=image, content_type="image/png"
        )
        cls.author = User.objects.create(username="TestUser")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_slug",
        )
        cls.post = Post.objects.create(
            text="Тестовый текст",
            author=cls.author,
            group=cls.group,
            image=cls.uploaded,
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_error_page(self):
        """Проверка работы кастомной страницы 404."""
        response = self.author_client.get("/nonexist-page/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, "core/404.html")

    def test_picture_in_post(self):
        """Проверка создания поста с картинкой."""
        url_list = {
            reverse("posts:index"),
            reverse("posts:group_list", args=[self.post.group]),
            reverse("posts:post_detail", args=[self.post.pk]),
            reverse("posts:profile", args=[self.post.author]),
        }
        for urls in url_list:
            with self.subTest(urls=urls):
                self.assertEqual(Post.objects.count(), self.post_count + 1)
                self.assertTrue(
                    Post.objects.filter(
                        author=self.post.author,
                        text=self.post.text,
                        group=self.post.group,
                        image=self.post.image,
                    ).exists()
                )
