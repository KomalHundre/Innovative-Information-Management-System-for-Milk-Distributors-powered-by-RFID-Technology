from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add-farmer/', views.add_farmer, name='add_farmer'),
    path('add-collection/', views.add_collection, name='add_collection'),
    path('weekly-report/', views.weekly_report, name='weekly_report'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('farmer-list/', views.farmer_list, name='farmer_list'),
] 