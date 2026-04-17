from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages

from accounts.utils import verified_required
from transactions.models import IssueRecord, ReadingProgress
from .models import Book, Category
from .forms import BookForm


# 🔒 ADMIN CHECK
def is_admin(user):
    return user.role == 'admin' or user.is_superuser


# =========================
# 👤 USER SIDE
# =========================

@login_required
@verified_required
def user_dashboard(request):
    return render(request, 'user/dashboard.html')


@login_required
@verified_required
def my_books(request):
    issued_books = IssueRecord.objects.filter(
        user=request.user,
        returned=False
    )

    books_with_progress = []

    for issue in issued_books:
        progress = ReadingProgress.objects.filter(
            user=request.user,
            book=issue.book
        ).first()

        current_page = progress.current_page if progress else 1
        total_pages = issue.book.total_pages or 1

        percent = int((current_page / total_pages) * 100)

        books_with_progress.append({
            'book': issue.book,
            'progress': percent,
            'issue_id': issue.id
        })

    return render(request, 'books/shelf.html', {
        'books': books_with_progress
    })


@login_required
@verified_required
def all_books(request):
    query = request.GET.get('q')
    category_id = request.GET.get('category')

    books = Book.objects.all()
    categories = Category.objects.all()

    if query:
        books = books.filter(title__icontains=query)

    if category_id:
        books = books.filter(category_id=category_id)

    return render(request, 'books/all_books.html', {
        'books': books,
        'categories': categories,
        'query': query,
        'selected_category': category_id
    })


# =========================
# 🔥 ADMIN PANEL
# =========================

@login_required
@verified_required
def admin_books(request):
    if not is_admin(request.user):
        return HttpResponseForbidden("Not allowed")

    books = Book.objects.all().order_by('-id')

    return render(request, 'admin/books_list.html', {
        'books': books
    })


# ➕ ADD BOOK
@login_required
@verified_required
def add_book(request):
    if not is_admin(request.user):
        return HttpResponseForbidden("Not allowed")

    form = BookForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        book = form.save(commit=False)

        # ✅ ALWAYS set available = total for new book
        book.available_copies = book.total_copies

        book.save()

        messages.success(request, "Book added successfully")
        return redirect('/books/admin/')

    return render(request, 'admin/book_form.html', {
        'form': form,
        'title': 'Add Book'
    })


# ✏️ EDIT BOOK
@login_required
@verified_required
def edit_book(request, book_id):
    if not is_admin(request.user):
        return HttpResponseForbidden("Not allowed")

    book = get_object_or_404(Book, id=book_id)

    form = BookForm(request.POST or None, request.FILES or None, instance=book)

    if form.is_valid():
        updated_book = form.save(commit=False)

        # ✅ FIX: prevent available > total
        if updated_book.available_copies > updated_book.total_copies:
            updated_book.available_copies = updated_book.total_copies

        updated_book.save()

        messages.success(request, "Book updated successfully")
        return redirect('/books/admin/')

    return render(request, 'admin/book_form.html', {
        'form': form,
        'title': 'Edit Book'
    })


# ❌ DELETE BOOK
@login_required
@verified_required
def delete_book(request, book_id):
    if not is_admin(request.user):
        return HttpResponseForbidden("Not allowed")

    book = get_object_or_404(Book, id=book_id)

    # ❌ BLOCK DELETE IF ISSUED
    if IssueRecord.objects.filter(book=book, returned=False).exists():
        messages.error(request, "Cannot delete. Book is currently issued.")
        return redirect('/books/admin/')

    if request.method == "POST":
        book.delete()
        messages.success(request, "Book deleted successfully")
        return redirect('/books/admin/')

    return render(request, 'admin/delete_confirm.html', {
        'book': book
    })