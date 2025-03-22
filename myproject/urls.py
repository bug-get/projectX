from django.urls import path, include
from django.contrib import admin
urlpatterns = [
    path('accounts/', include('accounts.urls')),
    path('admin/', admin.site.urls),
    # другие маршруты
]