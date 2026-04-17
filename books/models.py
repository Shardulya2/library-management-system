from django.db import models
from pypdf import PdfReader


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    isbn = models.CharField(max_length=20, unique=True, null=True, blank=True)

    cover = models.ImageField(upload_to='covers/')
    pdf_file = models.FileField(upload_to='books/')

    total_pages = models.IntegerField(default=0)

    # 🔥 STOCK SYSTEM
    total_copies = models.IntegerField(default=1)
    available_copies = models.IntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        # ✅ FIX STOCK LOGIC BEFORE SAVE
        if self.available_copies > self.total_copies:
            self.available_copies = self.total_copies

        # FIRST SAVE (important)
        super().save(*args, **kwargs)

        # ✅ PDF PAGE COUNT (only once)
        if self.pdf_file and self.total_pages == 0:
            try:
                reader = PdfReader(self.pdf_file.path)
                self.total_pages = len(reader.pages)

                super().save(update_fields=['total_pages'])
            except Exception as e:
                print("PDF read error:", e)

    def __str__(self):
        return self.title