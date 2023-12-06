import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm

from ..models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="TestUser")
        cls.group = Group.objects.create(
            title="Тест группа",
            slug="test_slug",
            description="Описание",
        )
        cls.image = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        cls.uploaded = SimpleUploadedFile(
            name="smallFORM.png", content=cls.image, content_type="image/png"
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый текст",
            group=cls.group,
            image=cls.uploaded,
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)

    def test_create_post_forms(self):
        """Проверка формы создания поста."""
        post_count = Post.objects.count()
        form_data = {
            "text": self.post.text,
            "group": self.group.pk,
            "image": self.image,
        }
        response = self.authorized_user.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertRedirects(
            response, reverse("posts:profile", args=(self.post.author,))
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=self.post.author,
                text=self.post.text,
                group=self.post.group,
                image=self.post.image,
            ).exists()
        )

    def test_post_edit_form_show_correct_context(self):
        """Шаблон post edit сформирован с правильным контекстом."""
        response = self.authorized_user.get(
            reverse(
                "posts:post_edit",
                args={
                    self.post.pk,
                },
            )
        )
        self.assertEqual(response.context["post"], self.post)
        self.assertEqual(response.context["is_edit"], True)
