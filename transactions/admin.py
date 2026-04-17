from django.contrib import admin
from .models import BookRequest, IssueRecord

admin.site.register(BookRequest)
admin.site.register(IssueRecord)