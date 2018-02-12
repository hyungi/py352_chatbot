from django.contrib import admin
from .models import Requirement, CrawlerData, NewsRecord, UserStatus

admin.site.register(Requirement)
admin.site.register(CrawlerData)
admin.site.register(NewsRecord)
admin.site.register(UserStatus)

# Register your models here.
