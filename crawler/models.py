from django.db import models
from django.utils import timezone
# Create your models here.


class Document(models.Model):
    # author = models.ForeignKey(
    #        'auth.User',
    #        on_delete=models.DO_NOTHING,
    #        )
    document_id = models.CharField(
        max_length=50,
        primary_key=True,
    )
    press = models.CharField(max_length=100, null=True)
    category = models.CharField(max_length=50, null=True)
    published_date = models.DateTimeField(default=timezone.now)
    crawled_date = models.DateTimeField(default=timezone.now)
    title = models.TextField()
    text = models.TextField()
    link = models.URLField(default="https://")

    def __str__(self):
        return self.press + ", " + self.title


class DocumentSummary(models.Model):
    document_id = models.OneToOneField(
        Document,
        on_delete=models.CASCADE,
        primary_key=True)
    sentences_n = models.IntegerField()
    text_rank = models.TextField()
    # top_word = models.TextField()
    word_count = models.TextField()
    word_tfidf = models.TextField()
    summary_text = models.TextField()


class SentimentList(models.Model):
    document_id = models.OneToOneField(
        Document,
        on_delete=models.CASCADE,
        primary_key=True)
    good = models.IntegerField()
    warm = models.IntegerField()
    sad = models.IntegerField()
    angry = models.IntegerField()
    want = models.IntegerField()


class Comment(models.Model):
    document_id = models.OneToOneField(
        Document,
        on_delete=models.CASCADE,
        primary_key=True)
    user_id = models.CharField(max_length=100, default="")
    content = models.TextField()
    published_date = models.DateTimeField(default=timezone.now)
    crawled_date = models.DateTimeField(default=timezone.now)
    recomm = models.IntegerField()
    unrecomm = models.IntegerField()
