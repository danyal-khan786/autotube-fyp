from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_home, name='chat_home'),
    path('api/chat/', views.chat_api, name='chat_api'),
    path('session/<int:session_id>/', views.get_session_history, name='get_history'),
    path('search/', views.search_chats, name='search_chats')
]