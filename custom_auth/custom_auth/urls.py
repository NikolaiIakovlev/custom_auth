from django.contrib import admin
from django.urls import path
from accounts.views import (
    RegisterView, LoginView, LogoutView,
    UserProfileView, DeleteAccountView,
    RoleListView, PermissionListView, ResourceListView,
    MockBusinessView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/profile/', UserProfileView.as_view(), name='profile'),
    path('api/delete-account/', DeleteAccountView.as_view(), name='delete-account'),
    path('api/roles/', RoleListView.as_view(), name='roles'),
    path('api/permissions/', PermissionListView.as_view(), name='permissions'),
    path('api/resources/', ResourceListView.as_view(), name='resources'),
    path('api/business-data/', MockBusinessView.as_view(), name='business-data'),
]