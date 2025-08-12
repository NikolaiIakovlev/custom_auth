from django.contrib import admin
from django.urls import path
# from accounts.views import (
#     RegisterView, LoginView, LogoutView,
#     UserProfileView, DeleteAccountView,
#     RoleListView, BusinessElementListView,
#     AccessRoleRuleListView, UserRoleListView, 
# )

urlpatterns = [
    path('admin/', admin.site.urls),
]