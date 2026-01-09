from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('profile/<int:user_id>/', views.public_profile_view, name='public_profile'),
    path('users/', views.user_list_view, name='user_list'),
    path('messages/group/create/', views.create_group_chat_view, name='create_group_chat'),
    path('messages/', views.conversation_list_view, name='conversation_list'),
    path('messages/<int:conversation_id>/', views.conversation_detail_view, name='conversation_detail'),
    path('messages/chat/<int:user_id>/', views.start_private_chat_view, name='start_private_chat'),
]