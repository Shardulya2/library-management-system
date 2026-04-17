from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
import json

from books.models import Book
from transactions.models import IssueRecord, ReadingProgress


@login_required
def read_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    issued = IssueRecord.objects.filter(
        user=request.user,
        book=book,
        returned=False
    ).exists()

    if not issued:
        return HttpResponseForbidden("You are not allowed to access this book")

    progress, _ = ReadingProgress.objects.get_or_create(
        user=request.user,
        book=book
    )

    return render(request, 'reader/viewer.html', {
        'book': book,
        'last_page': progress.current_page
    })


@login_required
def save_progress(request, book_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid'}, status=400)

    data = json.loads(request.body)
    page = data.get('page', 1)

    progress, _ = ReadingProgress.objects.get_or_create(
        user=request.user,
        book_id=book_id
    )

    progress.current_page = page
    progress.save()

    return JsonResponse({'status': 'saved'})