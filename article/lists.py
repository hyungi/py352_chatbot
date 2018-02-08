# -*- coding: utf-8 -*-
from crawler.models import PoliticsDocument, EconomicsDocument, SocietyDocument, \
    CultureLivingDocument, WorldDocument, ITScienceDocument
from django.utils import timezone

category_list = ['정치', '경제', '사회', '생활/문화', '세계', 'IT/과학']
press_list = []
date_list = []

for i in range(0, 7):
    date_list.append((timezone.now() - timezone.timedelta(days=i)).strftime("%Y-%m-%d"))

try:
    press_list.extend(list(PoliticsDocument.objects.values_list("press", flat=True).distinct()))
    press_list.extend(list(EconomicsDocument.objects.values_list("press", flat=True).distinct()))
    press_list.extend(list(SocietyDocument.objects.values_list("press", flat=True).distinct()))
    press_list.extend(list(CultureLivingDocument.objects.values_list("press", flat=True).distinct()))
    press_list.extend(list(WorldDocument.objects.values_list("press", flat=True).distinct()))
    press_list.extend(list(ITScienceDocument.objects.values_list("press", flat=True).distinct()))
    press_list = list(set(press_list))
    press_list.sort()

except Exception as e:
    press_list = ['조선일보', '중앙일보', '동아일보', '경향신문', '한겨레', '한국경제', '매일경제']

else:
    press_list.extend(list(PoliticsDocument.objects.values_list("press", flat=True).distinct()))
    press_list.extend(list(EconomicsDocument.objects.values_list("press", flat=True).distinct()))
    press_list.extend(list(SocietyDocument.objects.values_list("press", flat=True).distinct()))
    press_list.extend(list(CultureLivingDocument.objects.values_list("press", flat=True).distinct()))
    press_list.extend(list(WorldDocument.objects.values_list("press", flat=True).distinct()))
    press_list.extend(list(ITScienceDocument.objects.values_list("press", flat=True).distinct()))
    press_list = list(set(press_list))
    press_list.sort()
try:
    for i in range(0, 7):
        category_list.extend(list(PoliticsDocument.objects.filter(published_date__exact=timezone.datetime(int(date_list[i][0:4]), int(date_list[i][6:7]), int(date_list[i][9:10]))).values_list('category',flat=True).distinct()))
        category_list.extend(list(SocietyDocument.objects.filter(published_date__exact=timezone.datetime(int(date_list[i][0:4]), int(date_list[i][6:7]), int(date_list[i][9:10]))).values_list('category',flat=True).distinct()))
        category_list.extend(list(EconomicsDocument.objects.filter(published_date__exact=timezone.datetime(int(date_list[i][0:4]), int(date_list[i][6:7]), int(date_list[i][9:10]))).values_list('category',flat=True).distinct()))
        category_list.extend(list(CultureLivingDocument.objects.filter(published_date__exact=timezone.datetime(int(date_list[i][0:4]), int(date_list[i][6:7]), int(date_list[i][9:10]))).values_list('category',flat=True).distinct()))
        category_list.extend(list(ITScienceDocument.objects.filter(published_date__exact=timezone.datetime(int(date_list[i][0:4]), int(date_list[i][6:7]), int(date_list[i][9:10]))).values_list('category',flat=True).distinct()))
        category_list.extend(list(WorldDocument.objects.filter(published_date__exact=timezone.datetime(int(date_list[i][0:4]), int(date_list[i][6:7]), int(date_list[i][9:10]))).values_list('category',flat=True).distinct()))

    category_list = list(set(category_list))
except Exception as e:
    category_list = ['정치', '경제', '사회', '생활/문화', '세계', 'IT/과학']

else:
    for i in range(0, 7):
        category_list.extend(list(PoliticsDocument.objects.filter(
            published_date__exact=timezone.datetime(int(date_list[i][0:4]), int(date_list[i][6:7]),
                                                    int(date_list[i][9:10]))).values_list('category',
                                                                                          flat=True).distinct()))
        category_list.extend(list(SocietyDocument.objects.filter(
            published_date__exact=timezone.datetime(int(date_list[i][0:4]), int(date_list[i][6:7]),
                                                    int(date_list[i][9:10]))).values_list('category',
                                                                                          flat=True).distinct()))
        category_list.extend(list(EconomicsDocument.objects.filter(
            published_date__exact=timezone.datetime(int(date_list[i][0:4]), int(date_list[i][6:7]),
                                                    int(date_list[i][9:10]))).values_list('category',
                                                                                          flat=True).distinct()))
        category_list.extend(list(CultureLivingDocument.objects.filter(
            published_date__exact=timezone.datetime(int(date_list[i][0:4]), int(date_list[i][6:7]),
                                                    int(date_list[i][9:10]))).values_list('category',
                                                                                          flat=True).distinct()))
        category_list.extend(list(ITScienceDocument.objects.filter(
            published_date__exact=timezone.datetime(int(date_list[i][0:4]), int(date_list[i][6:7]),
                                                    int(date_list[i][9:10]))).values_list('category',
                                                                                          flat=True).distinct()))
        category_list.extend(list(WorldDocument.objects.filter(
            published_date__exact=timezone.datetime(int(date_list[i][0:4]), int(date_list[i][6:7]),
                                                    int(date_list[i][9:10]))).values_list('category',
                                                                                          flat=True).distinct()))
    category_list = list(set(category_list))