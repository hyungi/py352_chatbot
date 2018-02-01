# -*- coding: utf-8 -*-

from article.lists import *
from .models import *
'''
/crawler/getNews.py

'''


def getNews(input_press, input_year, input_month, input_day, input_category):

    '''
    :params
    고객이 입력한 press, date, category 정보를 바탕으로
    이에 맞는 뉴스 정보를 되돌려주는 함수(최신 10개 기사)
    
    :returns
    쿼리문에 의해 골라진 쿼리셋을
    response = {'key','value'}  key = document_id / value = title
    위와 같은 형태로 저장하여 전송한다.
    '''
    
    document = Document.objects.filter(press=input_press)
    document = document.filter(category=input_category)
    document = document.filter(published_date__year=input_year)
    document = document.filter(published_date__month=input_month)
    document = document.filter(published_date__day=input_day).order_by("-published_date")[:10]  # 최신순 10개를 보여주기 위함.

    return_document = document.values('document_id', 'title')
    document_list = list(return_document)
    doc_list_len = len(document_list)

    response = {}

    if doc_list_len == 0:
        print("선택한 뉴스가 없습니다.")
        response["none"] = "선택한 뉴스가 없습니다."

    for i in range(doc_list_len):
        response[document_list[i]['document_id']] = document_list[i]['title']

    return response


def get_summary(input_title):
    document_id = Document.objects.get(title=input_title)
    summary_document = DocumentSummary.objects.get(document_id=document_id)

    return document_id.title, summary_document.summary_text, document_id.link
