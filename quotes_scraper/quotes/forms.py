from django import forms
from .models import Quote, Tag, Author


class QuoteForm(forms.ModelForm):
    author = forms.CharField(max_length=100, label='Author')  # Замість ForeignKey поля
    tags = forms.CharField(max_length=255, label='Tags', help_text='Enter tags separated by commas')

    class Meta:
        model = Quote
        fields = ['quote']

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['fullname', 'born_date', 'born_location', 'description']

class TagSearchForm(forms.Form):
    tag = forms.CharField(label='Search by tag', max_length=100)