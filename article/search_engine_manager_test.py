import numpy as np
from article.search_engine_manager import search_engine_manager
from django.utils import timezone
from crawler.models import DocumentId

path = {"dtm_path": "dtm.txt",
        "matrix_path": "vctr"}

engine = search_engine_manager(**path)  # 두고두고 유지할 파일이니 파일 경로는 이쁘게!
doc_id_list = list(DocumentId.objects.all().values_list('document_id', flat=True))[0:5000]
engine.add_new_document(doc_id_list)  # 1,2,3,4,5는 document_id 대신 테스트용으로 입력한 id
# get_document_tfvector() 함수 이전 content_based_cf 처럼 수정해서 사용하시면 되겠습니다.
# 매번 크롤링이 완료된 후 위의 2행을 실행시켜주세요. (지금 실행할 땐, 이전 document_id들도 넣어서 한번 돌려주세요.


# 검색할 땐 위 과정 중에 add_new_document 없이 engine 변수만 만들고 바로 하시면 됩니다.
search_query = "대통령"
search_result = engine.search_news_document(search_query)
print(search_result)

search_query = "이재용 삼성전자 부회장"
search_result = engine.search_news_document(search_query)
print(search_result)

