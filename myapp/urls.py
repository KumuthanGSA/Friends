from django.urls import path
# Third part imports
from rest_framework_simplejwt.views import TokenRefreshView
# Local imports
from .views import LoginView, LogoutView, AdminRegisterView, SearchView, FriendRequestViewSet, FriendsListView

urlpatterns = [
    path('login', LoginView.as_view()),
    path('refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout', LogoutView.as_view()),
    path('register', AdminRegisterView.as_view()),
    path('search', SearchView.as_view()),
    path('friend-requests', FriendRequestViewSet.as_view(), name='friend-requests'),
    path('friend-requests/<int:pk>', FriendRequestViewSet.as_view(), name='friend-request-detail'),
    path('friends', FriendsListView.as_view(), name='friends-list'),
]