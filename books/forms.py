from django import forms
from .models import Book


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title',
            'author',
            'category',
            'isbn',
            'cover',
            'pdf_file',
            'total_copies',
            'available_copies'
        ]

    def clean(self):
        cleaned_data = super().clean()
        total = cleaned_data.get('total_copies')
        available = cleaned_data.get('available_copies')

        if available > total:
            raise forms.ValidationError("Available copies cannot exceed total copies")

        return cleaned_data