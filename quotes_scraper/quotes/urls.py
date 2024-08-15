from . import views
from django.urls import path, include

app_name = "quotes"

urlpatterns = [
    path('', views.main, name="root"),
    path("<int:page>/", views.main, name="root_paginate"),
    path('authors/', views.author_list, name='author_list'),
    path('author/<int:author_id>/', views.author_detail, name='author_detail'),
    path('add-author/', views.add_author, name='add_author'),
    path('add-quote/', views.add_quote, name='add_quote'),
    path('quotes/', views.quote_list, name='quote_list'),
    path('tags/<int:pk>/', views.tag_detail, name='tag_detail'),
    path('search/', views.search_quotes_by_tag, name='search'),
    path('top-tags/', views.top_tags, name='top_tags'),
    path('quotes/tag/<str:tag_name>/', views.search_quotes_by_tag, name='search_by_tag'),  # Пошук за ім'ям тега
]
