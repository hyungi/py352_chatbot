from .models import *

'''
/crawler/getNews.py

'''

def getNews(inputPress,inputYear,inputMonth,inputDay,inputCategory):

    '''
    :params
    고객이 입력한 press, date, category 정보를 바탕으로
    이에 맞는 뉴스 정보를 되돌려주는 함수
    
    :returns
    쿼리문에 의해 골라진 쿼리셋을 list 자료형으로 
    casting 하여 한 기사별로 출력한다.
    '''
    
    document = Document.objects.filter(press=inputPress)
    document = document.filter(category=inputCategory)
    document = document.filter(published_date__year=inputYear)
    document = document.filter(published_date__month=inputMonth)
    document = document.filter(published_date__day=inputDay)
    doc_id_list = document.all()

    return_document = document.values('press', 'title', 'category')
    document_list = list(return_document)
    doc_list_len = len(document_list)
    for i in range(doc_list_len):
        docsummary = DocumentSummary.objects.filter(document_id=doc_id_list[i])
        print(document_list[i]['press']+", "+document_list[i]['title']+", "+document_list[i]['category'])
        docsummary = list(docsummary.values('summary_text'))
        print(docsummary[0]['summary_text'])
