from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dairy/', include('dairy_collection.urls', namespace='dairy_collection')),
    path('', lambda request: redirect('dairy_collection:dashboard'), name='root'),
] 