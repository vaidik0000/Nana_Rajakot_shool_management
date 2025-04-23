from django.urls import path
from . import views

app_name = 'fees'

urlpatterns = [
    path('', views.fee_payment_list, name='fee_payment_list'),
    path('pay/', views.initiate_payment, name='initiate_payment'),
    path('pay/<int:student_id>/', views.initiate_payment, name='initiate_payment'),
    path('payment_callback/', views.payment_callback, name='payment_callback'),
    path('webhook/', views.webhook_handler, name='webhook_handler'),
    path('payment_success/<int:transaction_id>/', views.payment_success, name='payment_success'),
    path('payment_failure/', views.payment_failure, name='payment_failure'),
] 