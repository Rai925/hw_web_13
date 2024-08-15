from django.db import models


# Create your models here.
class Author(models.Model):
    fullname = models.CharField(max_length=100)
    born_date = models.DateField(null=True, blank=True)
    born_location = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    see_also = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.fullname

    @property
    def quotes(self):
        return self.quote_set.all()



class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    def quote_count(self):
        return self.quote_set.count()


class Quote(models.Model):
    quote = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='quotes', default=1)
    tags = models.ManyToManyField(Tag, related_name='quotes')
