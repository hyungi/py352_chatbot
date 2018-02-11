from django.contrib import admin
from .models import Requirement, CrawlerData, NewsRequirement, UserStatus

admin.site.register(Requirement)
admin.site.register(CrawlerData)
admin.site.register(NewsRequirement)
admin.site.register(UserStatus)

# Register your models here.
