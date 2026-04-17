from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseForbidden

from accounts.utils import verified_required
from books.models import Book
from .models import BookRequest, IssueRecord


# 🔒 ADMIN CHECK
def is_admin(user):
    return user.role == 'admin' or user.is_superuser


# 🔹 REQUEST BOOK
@login_required
@verified_required
def request_book(request, book_id):
    if request.method != 'POST':
        return HttpResponseForbidden("Invalid request")

    book = get_object_or_404(Book, id=book_id)

    # ❌ STOCK CHECK
    if book.available_copies <= 0:
        messages.error(request, "No copies available")
        return redirect('/books/')

    # ❌ Already issued
    if IssueRecord.objects.filter(
        user=request.user,
        book=book,
        returned=False
    ).exists():
        messages.warning(request, "Already in your library")
        return redirect('/books/')

    # ❌ Already pending
    if BookRequest.objects.filter(
        user=request.user,
        book=book,
        status='pending'
    ).exists():
        messages.info(request, "Request already pending")
        return redirect('/books/')

    # ✅ Create request
    BookRequest.objects.create(user=request.user, book=book)

    messages.success(request, "Request submitted")
    return redirect('/books/')


# 🔹 APPROVE REQUEST
@login_required
@verified_required
@transaction.atomic
def approve_request(request, request_id):
    if not is_admin(request.user):
        return HttpResponseForbidden("Not allowed")

    req = get_object_or_404(BookRequest, id=request_id)
    book = req.book

    if req.status == 'approved':
        messages.info(request, "Already approved")
        return redirect('/transactions/admin-dashboard/')

    # ❌ STOCK CHECK
    if book.available_copies <= 0:
        messages.error(request, "No copies available")
        return redirect('/transactions/admin-dashboard/')

    # ❌ Already issued
    if IssueRecord.objects.filter(
        user=req.user,
        book=book,
        returned=False
    ).exists():
        messages.warning(request, "Already issued")
        return redirect('/transactions/admin-dashboard/')

    # ✅ REDUCE STOCK
    book.available_copies -= 1
    book.save()

    # ✅ Approve request
    req.status = 'approved'
    req.save()

    # ✅ Create issue record
    IssueRecord.objects.create(
        user=req.user,
        book=book
    )

    messages.success(request, "Book issued successfully")
    return redirect('/transactions/admin-dashboard/')


# 🔹 REJECT REQUEST
@login_required
@verified_required
def reject_request(request, request_id):
    if not is_admin(request.user):
        return HttpResponseForbidden("Not allowed")

    req = get_object_or_404(BookRequest, id=request_id)

    if req.status == 'rejected':
        messages.info(request, "Already rejected")
        return redirect('/transactions/admin-dashboard/')

    req.status = 'rejected'
    req.save()

    messages.info(request, "Request rejected")
    return redirect('/transactions/admin-dashboard/')


# 🔹 RETURN BOOK (WITH STOCK FIX)
@login_required
@verified_required
def return_book(request, issue_id):
    issue = get_object_or_404(IssueRecord, id=issue_id)
    book = issue.book

    # 🔐 Only owner or admin
    if not (issue.user == request.user or is_admin(request.user)):
        return HttpResponseForbidden("Not allowed")

    if issue.returned:
        messages.warning(request, "Already returned")
        return redirect('/books/my-books/')

    # ✅ mark returned
    issue.returned = True
    issue.save()

    # ✅ INCREASE STOCK BACK
    book.available_copies += 1
    book.save()

    messages.success(request, "Book returned successfully")

    if is_admin(request.user):
        return redirect('/transactions/admin-dashboard/')
    else:
        return redirect('/books/my-books/')


# 🔹 USER REQUESTS PAGE
@login_required
@verified_required
def my_requests(request):
    requests = BookRequest.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(request, 'transactions/my_requests.html', {
        'requests': requests
    })


# 🔹 ADMIN DASHBOARD (UPDATED WITH BOOKS)
@login_required
@verified_required
def admin_dashboard(request):

    if not is_admin(request.user):
        return redirect('/accounts/admin-login/')

    pending = BookRequest.objects.filter(status='pending')
    issued = IssueRecord.objects.filter(returned=False)
    books = Book.objects.all().order_by('-id')

    return render(request, 'admin/dashboard.html', {
        'pending': pending,
        'issued': issued,
        'books': books,

        'total_requests': BookRequest.objects.count(),
        'pending_count': pending.count(),
        'approved_count': BookRequest.objects.filter(status='approved').count(),
        'rejected_count': BookRequest.objects.filter(status='rejected').count(),
        'issued_count': issued.count(),
    })