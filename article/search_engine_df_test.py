import numpy as np
import article.search_engine_df as sedf
from crawler.get_news import get_latest_news_id_list

path = {"docu_info_path": "./search/docu_info",
        "division_path": "./search/division"}
engine = sedf.search_engine_manager(**path) #두고두고 유지할 파일이니 파일 경로는 이쁘게!

doc_id_list = get_latest_news_id_list(0, 5000)
engine.add_new_document(doc_id_list) #1,2,3,4,5는 document_id 대신 테스트용으로 입력한 id
# engine.add_new_document([4,5]) #1,2,3,4,5는 document_id 대신 테스트용으로 입력한 id

search_query = "대통령"
search_result = engine.search_news_document(search_query)
print(search_result)

search_query = "이재용 삼성전자 부회장"
search_result = engine.search_news_document(search_query)
print(search_result)

