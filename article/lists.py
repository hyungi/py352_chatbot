# -*- coding: utf-8 -*-
from crawler.models import PoliticsDocument, EconomicsDocument, SocietyDocument, \
    CultureLivingDocument, WorldDocument, ITScienceDocument


menu_list = ['신문사 고르기', '날짜 고르기', '분야 고르기']
year_list = ['2015','2016','2017','2018']
month_list = ['1','2','3','4','5','6','7','8','9','10','11','12']
day_list = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']
press_list = []
category_list = ['정치', '경제', '사회', '생활/문화', '세계', 'IT/과학']

try:
    press_list.extend(list(PoliticsDocument.objects.values_list("press", flat=True).distinct()))
    press_list.extend(list(EconomicsDocument.objects.values_list("press", flat=True).distinct()))
    press_list.extend(list(SocietyDocument.objects.values_list("press", flat=True).distinct()))
    press_list.extend(list(CultureLivingDocument.objects.values_list("press", flat=True).distinct()))
    press_list.extend(list(WorldDocument.objects.values_list("press", flat=True).distinct()))
    press_list.extend(list(ITScienceDocument.objects.values_list("press", flat=True).distinct()))
    press_set = set(press_list)
    press_list = list(press_set)
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
    press_set = set(press_list)
    press_list = list(press_set)
    press_list.sort()
