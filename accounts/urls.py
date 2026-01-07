from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('users/', views.user_list_view, name='user_list'),
    path('profile/<int:user_id>/', views.public_profile_view, name='public_profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
]
