from django.contrib import admin
from crawler.models import Document, DocumentSummary, SentimentList, Comment

admin.site.register(Document)
admin.site.register(DocumentSummary)
admin.site.register(SentimentList)
admin.site.register(Comment)

# Register your models here.
