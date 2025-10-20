from django.urls import path

from api.user.views.auth_view import RefreshView, SocialAuthView

urlpatterns = [
    path(
        "<str:provider>/login/",
        SocialAuthView.as_view({"post": "create"}),
        name="social-login",
    ),
    path(
        "withdraw/",
        SocialAuthView.as_view({"delete": "withdraw"}),
        name="withdraw",
    ),
    path("refresh/", RefreshView.as_view({"post": "refresh"}), name="token_refresh"),
]
