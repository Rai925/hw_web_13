from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

app_name = 'quotes_scraper'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('quotes.urls', namespace='quotes')),
    path('users/', include('users.urls')),
    path('accounts/', include('allauth.urls'))
]
