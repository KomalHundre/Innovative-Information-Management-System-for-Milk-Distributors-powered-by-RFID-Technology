from django.urls import path
from . import views

app_name = 'dairy_collection'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('farmers/', views.farmer_list, name='farmer_list'),
    path('farmer/add/', views.farmer_add, name='farmer_add'),
    path('farmer/<int:farmer_id>/edit/', views.farmer_edit, name='farmer_edit'),
    path('farmer/<int:farmer_id>/delete/', views.farmer_delete, name='farmer_delete'),
    path('profile/edit/', views.farmer_profile_edit, name='farmer_profile_edit'),
    path('collection/create/', views.milk_collection_create, name='milk_collection_create'),
    path('collection/', views.collection_list, name='collection_list'),
    path('report/generate/', views.generate_weekly_report, name='generate_weekly_report'),
    path('report/<int:report_id>/', views.report_detail, name='report_detail'),
    path('reports/farmers/', views.farmer_reports, name='farmer_reports'),
    path('reports/farmer/<int:farmer_id>/', views.farmer_report, name='farmer_report'),
    path('reports/farmer/<int:farmer_id>/pdf/', views.farmer_report_pdf, name='farmer_report_pdf'),
    path('notifications/', views.notifications_list, name='notifications'),
    path('get-price/<str:fat_content>/', views.get_price, name='get_price'),
    path('payments/', views.payment_history, name='payment_history'),
    path('payments/initiate/', views.payment_initiate, name='payment_initiate'),
    path('payments/calculate/', views.calculate_payment, name='calculate_payment'),
    path('payments/create/', views.create_payment, name='create_payment'),
    path('payments/verify/', views.verify_payment, name='verify_payment'),
    path('payment/verify/', views.verify_payment, name='verify_payment'),
    path('payment/mock-process/', views.mock_process_payment, name='mock_process_payment'),
    path('send-report-sms/', views.send_report_sms, name='send_report_sms'),
    path('payment/history/', views.payment_history, name='payment_history'),
    path('payment/pending/', views.pending_payments, name='pending_payments'),
    path('payment/initiate/', views.payment_initiate, name='payment_initiate'),
    path('rfid-scan/', views.rfid_scan, name='rfid_scan'),
]