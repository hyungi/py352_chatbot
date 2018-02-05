from django.contrib import admin
from crawler.models import DocumentId, \
    PoliticsDocument, EconomicsDocument, SocietyDocument, \
    CultureLivingDocument, WorldDocument, ITScienceDocument, \
    DocumentSummary, SentimentList, Comment

admin.site.register(DocumentId)

admin.site.register(PoliticsDocument)
admin.site.register(EconomicsDocument)
admin.site.register(SocietyDocument)
admin.site.register(CultureLivingDocument)
admin.site.register(WorldDocument)
admin.site.register(ITScienceDocument)

admin.site.register(DocumentSummary)
admin.site.register(SentimentList)
admin.site.register(Comment)

# Register your models here.
