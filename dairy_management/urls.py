# Dairy Management System URL Configuration
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.utils import timezone
from datetime import timedelta

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dairy/', include('dairy_collection.urls', namespace='dairy_collection')),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('', include('milk.urls')), 
]

end_date = timezone.localtime().date()
start_date = end_date - timedelta(days=7)
