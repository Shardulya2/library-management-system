from django.urls import path
from . import views

urlpatterns = [
    path('request/<int:book_id>/', views.request_book),
    path('approve/<int:request_id>/', views.approve_request),
    path('reject/<int:request_id>/', views.reject_request),
    path('return/<int:issue_id>/', views.return_book),
    path('my-requests/', views.my_requests),
    path('admin-dashboard/', views.admin_dashboard),
]