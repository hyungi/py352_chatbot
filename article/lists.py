from crawler.models import *


menulist = ['신문사 고르기', '날짜 고르기', '분야 고르기']


try: 
    presslist = list(Document.objects.values_list("press", flat=True).distinct())
except Exception as e:
    presslist = ['조선','중앙','동아','경향','한겨레','한국경제','매일경제']
else:
    presslist = list(Document.objects.values_list("press", flat=True).distinct())

yearlist = ['2015','2016','2017','2018']
monthlist = ['1','2','3','4','5','6','7','8','9','10','11','12']
daylist = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']


try:
    categorylist = list(Document.objects.values_list("category", flat=True).distinct())
except Exception as e:
    categorylist= ['정치','경제','사회','생활/문화','세계','IT/과학','오피니언']
else:
    categorylist = list(Document.objects.values_list("category", flat=True).distinct())

