# -*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone
# Create your models here.
'''
crawler/models.py
'''


class DocumentId(models.Model):
    document_id = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.document_id


class Document(DocumentId):
    press = models.CharField(max_length=100, null=True)
    category = models.CharField(max_length=50, null=True)
    published_date = models.DateTimeField(default=timezone.now)
    crawled_date = models.DateTimeField(default=timezone.now)
    title = models.TextField()
    text = models.TextField()
    link = models.URLField(default="https://")

    class Meta:
        abstract = True


class PoliticsDocument(Document):

    def __str__(self):
        return "["+self.category+"] "+self.press+", "+self.title


class EconomicsDocument(Document):

    def __str__(self):
        return "["+self.category+"] "+self.press+", "+self.title


class SocietyDocument(Document):

    def __str__(self):
        return "["+self.category+"] "+self.press+", "+self.title


class CultureLivingDocument(Document):

    def __str__(self):
        return "["+self.category+"] "+self.press+", "+self.title


class WorldDocument(Document):

    def __str__(self):
        return "["+self.category+"] "+self.press+", "+self.title


class ITScienceDocument(Document):

    def __str__(self):
        return "["+self.category+"] "+self.press+", "+self.title


class DocumentSummary(models.Model):
    document_id = models.OneToOneField(
        DocumentId,
        on_delete=models.CASCADE,
        primary_key=True)
    sentences_n = models.IntegerField()
    text_rank = models.TextField()
    word_count = models.TextField()
    word_tfidf = models.TextField()
    summary_text = models.TextField()

    def __str__(self):
        return self.document_id.document_id


class SentimentList(models.Model):
    document_id = models.OneToOneField(
        DocumentId,
        on_delete=models.CASCADE,
        primary_key=True)
    good = models.IntegerField()
    warm = models.IntegerField()
    sad = models.IntegerField()
    angry = models.IntegerField()
    want = models.IntegerField()


class Comment(models.Model):
    document_id = models.OneToOneField(
        DocumentId,
        on_delete=models.CASCADE,
        primary_key=True)
    user_id = models.CharField(max_length=100, default="")
    content = models.TextField()
    published_date = models.DateTimeField(default=timezone.now)
    crawled_date = models.DateTimeField(default=timezone.now)
    recomm = models.IntegerField()
    unrecomm = models.IntegerField()
