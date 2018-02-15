# -*- coding: utf-8 -*-
from crawler.models import PoliticsDocument, EconomicsDocument, SocietyDocument, \
    CultureLivingDocument, WorldDocument, ITScienceDocument
from django.utils import timezone

category_list = ['정치', '경제', '사회', '생활/문화', '세계', 'IT/과학']
press_list = []
date_list = []
first_button_list = ['사용방법 익히기', '뉴스 선택하기', '최근에 본 뉴스 확인하기']

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

press_list.append('--------------------')

gender_list = ['남성', '여성']

birth_year_list = []

for i in range(1950, 2010):
    birth_year_list.append(str(i))

region_list = ['서울', '경기', '인천', '강원', '대전', '충북', '충남', '광주', '전북', '전남', '부산', '울산', '대구', '경북', '경남', '제주', '그 외']

agree_disagree_news_save_list = ['뉴스를 저장하겠습니다', '뉴스를 저장하지 않겠습니다.']