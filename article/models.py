# -*- coding: utf-8 -*-


from django.db import models
from django.utils import timezone

'''
/article/models.py

'''


class Requirement(models.Model):
    user_key = models.CharField(max_length=200, default="")
    press = models.CharField(max_length=200, default="")
    date = models.CharField(max_length=200, default="")
    category = models.CharField(max_length=200, default="")
    request_date = models.DateTimeField(default=timezone.now().strftime("%Y-%m-%d %H:%M"))

    def __str__(self):
        return self.press + ", " + self.date + ", " + self.category


class CrawlerData(models.Model):
    crawled_date = models.DateTimeField(default=timezone.now().strftime("%Y-%m-%d %H:%M"))

    def __str__(self):
        return self.crawled_date.strftime("%Y-%m-%d %H:%M")


class NewsRequirement(models.Model):
    user_key = models.CharField(max_length=200, default="")
    asked_news_title = models.CharField(max_length=200, default="")
    asked_time = models.DateTimeField(default=timezone.now().strftime("%Y-%m-%d %H:%M"))

    def __str__(self):
        return self.asked_news_title + ", " + self.asked_time.strftime("%Y-%m-%d %H:%M")
