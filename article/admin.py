from django.contrib import admin
from .models import Requirement, CrawlerData, NewsRecord, UserStatus, FeedBack

admin.site.register(Requirement)
admin.site.register(CrawlerData)
admin.site.register(NewsRecord)
admin.site.register(UserStatus)
admin.site.register(FeedBack)

# Register your models here.
