from django.urls import path
from . import views

urlpatterns = [
    path('telegram_login/', views.telegram_login, name='telegram_login'),
    path('profile/', views.profile, name='profile'),
]