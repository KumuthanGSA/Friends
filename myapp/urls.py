from django.urls import path
# Third part imports
from rest_framework_simplejwt.views import TokenRefreshView
# Local imports
from .views import LoginView, LogoutView, AdminRegisterView, SearchView

urlpatterns = [
    path('login', LoginView.as_view()),
    path('refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout', LogoutView.as_view()),
    path('register', AdminRegisterView.as_view()),
    path('search', SearchView.as_view())
]