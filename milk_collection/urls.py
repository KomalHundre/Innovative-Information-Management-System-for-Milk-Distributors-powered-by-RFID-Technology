from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('scan-rfid/', views.scan_rfid, name='scan_rfid'),
    path('get-farmer-details/<str:rfid>/', views.get_farmer_details, name='get_farmer_details'),
    path('collect-milk/', views.collect_milk, name='collect_milk'),
    path('weekly-report/', views.weekly_report, name='weekly_report'),
    path('process-payment/', views.process_payment, name='process_payment'),
]