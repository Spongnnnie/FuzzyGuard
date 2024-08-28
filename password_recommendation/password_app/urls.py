# password_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('api/generate_passwords/', views.generate_passwords, name='generate_passwords'),
    path('check_password_strength/', views.check_password_strength, name='check_password_strength'),
    # Other URL patterns...
]
