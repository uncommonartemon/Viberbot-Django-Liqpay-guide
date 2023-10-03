from django.urls import path
from . import views

urlpatterns = [
    path('api/sellers/', views.Sellers.as_view(), name='sellers'),
    path('api/seller/<str:seller>', views.Products.as_view(), name='products'),
    path('',views.webhook, name='viber_webhook'),
]

