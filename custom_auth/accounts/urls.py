from django.urls import path
from .views import (
    register_user, login_user, logout_user,
    update_profile, delete_account
)

app_name = 'accounts'


urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('update-profile/', update_profile, name='update_profile'),
    path('delete-account/', delete_account, name='delete_account'),
]
