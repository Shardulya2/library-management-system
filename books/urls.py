from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('my-books/', views.my_books, name='my_books'),
    path('', views.all_books, name='all_books'),

    # 🔥 ADMIN CRUD
    path('admin/', views.admin_books, name='admin_books'),
    path('admin/add/', views.add_book, name='add_book'),
    path('admin/edit/<int:book_id>/', views.edit_book, name='edit_book'),
    path('admin/delete/<int:book_id>/', views.delete_book, name='delete_book'),
]