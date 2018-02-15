import article.content_based_cf as cb

# 두고두고 유지할 파일이니 파일 경로는 이쁘게!
searcher = cb.news_searcher("temp2.txt")
# 1,2,3,4,5는 document_id 대신 테스트용으로 입력한 id
searcher.add_new_document(
    [99991636085856374016319605011998820755,
     99938510797515715116994082708390727525,
     99697504621368584423463722508110494257,
     99681750115330016465732018022180532228,
     99616144813817172513838121030912522843])

# 특정 document_id가 주어졌을 때 이와 가장 유사한 document 반환 (content-based 추천)
temp = searcher.get_similar_document(99991636085856374016319605011998820755, 1)
print(temp)

search_query = "문재인 대통령 평창 북한"
temp2 = searcher.search_news_document(search_query, 1)
print(temp2)

search_query2 = "아파트 대책 전용 부동산"
temp3 = searcher.search_news_document(search_query2, 1)
print(temp3)

#print(searcher.dtm_index)
#print(searcher.dtm_list)