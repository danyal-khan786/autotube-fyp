
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('AuthApp.urls')),
    path('', include('ToolkitApp.urls')),
    path('ai/', include('AIChatbotApp.urls')),
]
