from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('signin/', views.SignInView.as_view(), name='signin'),
    path('checkout-session/<str:id>/', views.create_checkout_session, name='checkout_session'),
    path('payment-cancelled', views.payment_cancelled, name='payment_cancelled'),
    path('payment-successful', views.payment_successful, name='payment_successful'),
    path('webhook', views.webhook, name='webhook'),
]