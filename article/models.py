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


class UserStatus(models.Model):
    user_key = models.CharField(max_length=200, default="")
    gender = models.CharField(max_length=4, default="")
    birth_year = models.PositiveSmallIntegerField(blank=True, null=True, default=0)
    location = models.CharField(max_length=200, default="")
    recommend_service = models.BooleanField(default=True)
    remove_seen_news = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user_key) + " " + self.gender + " " + str(self.birth_year) + " " + self.location


class NewsRecord(models.Model):
    request_news_id = models.CharField(max_length=50, default="")
    request_press = models.CharField(max_length=20, default="")
    request_category = models.CharField(max_length=20, default="")
    request_title = models.CharField(max_length=200, default="")
    request_time = models.DateTimeField(default=timezone.now().strftime("%Y-%m-%d %H:%M"))
    user_status = models.ForeignKey(UserStatus, on_delete=models.CASCADE, null=True)
    is_scraped = models.BooleanField(default=False)

    def __str__(self):
        return self.request_title + ", " + self.request_time.strftime("%Y-%m-%d %H:%M")


class FeedBack(models.Model):
    user_status = models.ForeignKey(UserStatus, on_delete=models.CASCADE, null=True)
    feedback_type = models.CharField(max_length=50, default="")
    feedback_content = models.TextField()
    # 별점을 매길수 있는 필드 추가하기
