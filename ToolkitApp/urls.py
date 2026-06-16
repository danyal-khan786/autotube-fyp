# created manually!
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('process/', views.process_video, name='process_video'),
    path('results/<int:pk>/', views.results_detail, name='results_detail'),
    path('results/<int:pk>/pdf/', views.download_pdf_report, name='download_pdf'),
]