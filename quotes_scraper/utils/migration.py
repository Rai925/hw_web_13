import os
import django
from pymongo import MongoClient

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "quotes_scraper.settings")
django.setup()

from quotes.models import Quote, Tag, Author  # noqa

# Підключення до MongoDB
client = MongoClient("mongodb://localhost")
db = client.homework

# Перенос авторів
authors = db.authors.find()
for author in authors:
    Author.objects.get_or_create(
        fullname=author['fullname'],
        born_date=author['born_date'],
        born_location=author['born_location'],
        description=author['description']
    )

# Перенос цитат
quotes = db.quotes.find()
for quote in quotes:
    tags = []
    for tag in quote['tags']:
        t, _ = Tag.objects.get_or_create(name=tag)
        tags.append(t)

    # Перевірка, чи існує цитата
    exist_quote = Quote.objects.filter(quote=quote['quote']).exists()

    if not exist_quote:
        author = db.authors.find_one({'_id': quote['author']})
        a = Author.objects.get(fullname=author['fullname'])
        q = Quote.objects.create(
            quote=quote['quote'],
            author=a
        )
        q.tags.add(*tags)
