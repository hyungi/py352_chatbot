from django.contrib import admin
from .models import Requirement, CrawlerData, NewsRequirement

admin.site.register(Requirement)
admin.site.register(CrawlerData)
admin.site.register(NewsRequirement)
# Register your models here.
