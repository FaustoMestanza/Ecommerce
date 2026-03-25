from django.urls import path

from .views import LoginView, MeView, PublicTokenRefreshView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="token_obtain_pair"),
    path("refresh/", PublicTokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="auth-me"),
]