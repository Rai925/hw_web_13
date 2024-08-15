import json
from pathlib import Path

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from .forms import TagSearchForm
from .utils import get_mongodb
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from .models import Author, Quote, Tag
from .forms import AuthorForm, QuoteForm
from django.db.models import Count

from django.contrib.auth.decorators import login_required


def main(request, page=1):
    db = get_mongodb()
    quotes = db.quotes.find()
    per_page = 10
    paginator = Paginator(list(quotes), per_page)
    quotes_on_page = paginator.page(page)
    return render(request, 'quotes/index.html', context={'quotes': quotes_on_page})


#
def author_list(request):
    authors = Author.objects.all()
    return render(request, 'quotes/author_list.html', {'authors': authors})


@login_required
def add_author(request):
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = AuthorForm()
    return render(request, 'quotes/add_author.html', {'form': form})


def tag_detail(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    quotes = tag.quotes.all()
    return render(request, 'quotes/tag_detail.html', {'tag': tag, 'quotes': quotes})


def author_detail(request, author_id):
    author = get_object_or_404(Author, id=author_id)
    quotes = author.quotes.all()
    return render(request, 'quotes/author_detail.html', {'author': author, 'quotes': quotes})


def quote_list(request):
    quotes = Quote.objects.all()
    return render(request, 'quotes/quote_list.html', {'quotes': quotes})


def top_tags(request):
    tags = Tag.objects.annotate(num_quotes=Count('quotes')).order_by('-num_quotes')[:10]
    return render(request, 'quotes/top_tags.html', {'tags': tags})


def search_quotes_by_tag(request):
    tag_name = request.GET.get('q')
    if tag_name:
        tag = Tag.objects.filter(name=tag_name).first()
        if tag:
            quotes = Quote.objects.filter(tags=tag).distinct()
        else:
            quotes = Quote.objects.none()
    else:
        quotes = Quote.objects.none()
    return render(request, 'quotes/quote_list.html', {'quotes': quotes})


def test_view(request):
    return HttpResponse('<h1>Test Page</h1>')


@login_required
def add_quote(request):
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            quote_text = form.cleaned_data['quote']
            author_name = form.cleaned_data['author']
            tags = form.cleaned_data['tags'].split(',')  # Розділення тегів

            # Обробка автора
            author, created = Author.objects.get_or_create(fullname=author_name)

            # Обробка тегів
            tag_objects = []
            for tag_name in tags:
                tag_name = tag_name.strip()  # Очищення пробілів
                tag, created = Tag.objects.get_or_create(name=tag_name)
                tag_objects.append(tag)

            # Створення нової цитати
            quote = Quote.objects.create(quote=quote_text, author=author)
            quote.tags.add(*tag_objects)

            return redirect('/')
    else:
        form = QuoteForm()
    return render(request, 'quotes/add_quote.html', {'form': form})
