from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register),
    path('verify/<int:user_id>/', views.verify_otp),

    path('user-login/', views.user_login),
    path('admin-login/', views.admin_login),

    path('logout/', views.logout_view),
]