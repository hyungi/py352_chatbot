# -*- coding: utf-8 -*-
from crawler.models import PoliticsDocument, EconomicsDocument, SocietyDocument, \
    CultureLivingDocument, WorldDocument, ITScienceDocument
from django.utils import timezone

category_list = ['정치', '경제', '사회', '생활/문화', '세계', 'IT/과학']
press_list = []
date_list = []
first_button_list = ['최신 뉴스 보기', '맞춤형 뉴스 큐레이팅', '뉴스 검색', '최근 본 뉴스', '저장한 뉴스', '메일링 서비스 신청하기', '사용 방법 보기']
news_select_button_list = ['날짜로 검색', '키워드로 검색', 'stop']

for i in range(0, 7):
    date_list.append((timezone.now() - timezone.timedelta(days=i)).strftime("%Y-%m-%d"))

date_list += ['직접 입력']

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

agree_disagree_news_save_list = ['스크랩 하기', '스크랩 하지 않음']

maintain_remove_news_save_list = ['유지하기', '삭제하기']

end_of_service_list = ['...목록으로', '...다시 검색하기', '...메인 메뉴로']

feedback_list = ['이용 후기', '오류 레포트', '건의사항']

setting_list = ['추천 서비스 이용 여부', '저장한 뉴스 초기화']
news_recomm_service_agree_disagree = ['추천 서비스를 이용하겠습니다', '추천 서비스를 이용하지 않겠습니다']
stars_list = ['5', '4', '3', '2', '1']
# stop > first_button_list/ break > date_list /continue > news_title_list
