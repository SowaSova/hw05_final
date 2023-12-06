from django.contrib.auth.views import (LoginView, LogoutView,
                                       PasswordChangeView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView)
from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path(
        "logout/",
        LogoutView.as_view(template_name="users/logged_out.html"),
        name="logout",
    ),
    path("signup/", views.sign_up, name="signup"),
    path(
        "login/",
        LoginView.as_view(
            template_name="users/login.html", redirect_authenticated_user=True
        ),
        name="login",
    ),
    path(
        "password_change/",
        PasswordChangeView.as_view(
            template_name="users/password_change_form.html"
        ),
        name="pswrd_change",
    ),
    path(
        "password_change/done/",
        views.PasswordChangeDone.as_view(
            template_name="users/password_change_done.html"
        ),
        name="pswrd_change_done",
    ),
    path(
        "password_reset/",
        views.PasswordReset.as_view(
            template_name="users/password_reset_form.html"
        ),
        name="pswrd_reset",
    ),
    path(
        "password_reset/done/",
        PasswordResetDoneView.as_view(
            template_name="users/password_reset_done.html"
        ),
        name="pswrd_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html"
        ),
        name="pswrd_reset_conf",
    ),
    path(
        "reset/done/",
        PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html"
        ),
        name="pswrd_reset_compl",
    ),
]
