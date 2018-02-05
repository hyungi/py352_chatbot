# -*- coding: utf-8 -*-

from .models import *
'''
/crawler/get_news.py

'''


def get_news(press, year, month, day, category):
    """
    :params
    고객이 입력한 press, year, month, day, category 정보를 바탕으로
    이에 맞는 뉴스 정보를 되돌려주는 함수(최신 10개 기사)
    :returns
    쿼리문에 의해 골라진 쿼리셋을
    response = {'key','value'}  value = title / key = document_id
    위와 같은 형태로 저장하여 전송한다.
    """

    if category == "정치":
        document = PoliticsDocument.objects.filter(press=press)
        document = document.filter(published_date__year=year)
        document = document.filter(published_date__month=month)
        document = document.filter(published_date__day=day).order_by("-published_date")[:10]  # 최신순 10개를 보여주기 위함.

    elif category == "경제":
        document = EconomicsDocument.objects.filter(press=press)
        document = document.filter(published_date__year=year)
        document = document.filter(published_date__month=month)
        document = document.filter(published_date__day=day).order_by("-published_date")[:10]  # 최신순 10개를 보여주기 위함.

    elif category == "사회":
        document = SocietyDocument.objects.filter(press=press)
        document = document.filter(published_date__year=year)
        document = document.filter(published_date__month=month)
        document = document.filter(published_date__day=day).order_by("-published_date")[:10]  # 최신순 10개를 보여주기 위함.

    elif category == "생활/문화":
        document = CultureLivingDocument.objects.filter(press=press)
        document = document.filter(published_date__year=year)
        document = document.filter(published_date__month=month)
        document = document.filter(published_date__day=day).order_by("-published_date")[:10]  # 최신순 10개를 보여주기 위함.

    elif category == "세계":
        document = WorldDocument.objects.filter(press=press)
        document = document.filter(published_date__year=year)
        document = document.filter(published_date__month=month)
        document = document.filter(published_date__day=day).order_by("-published_date")[:10]  # 최신순 10개를 보여주기 위함.

    elif category == "IT/과학":
        document = ITScienceDocument.objects.filter(press=press)
        document = document.filter(published_date__year=year)
        document = document.filter(published_date__month=month)
        document = document.filter(published_date__day=day).order_by("-published_date")[:10]  # 최신순 10개를 보여주기 위함.

    return_document = document.values('document_id', 'title')
    document_list = list(return_document)
    doc_list_len = len(document_list)

    response = {}

    if doc_list_len == 0:
        print("선택한 뉴스가 없습니다.")
        response["none"] = "선택한 뉴스가 없습니다."

    for i in reversed(range(doc_list_len)):
        response[document_list[i]['title']] = document_list[i]['document_id']
    # 임시방편이라 수정해야함

    return response


def get_summary(input_document_id, category):
    document_id = DocumentId.objects.get(document_id=input_document_id)

    if category == "정치":
        document = PoliticsDocument.objects.get(document_id=document_id)

    elif category == "경제":
        document = EconomicsDocument.objects.get(document_id=document_id)

    elif category == "사회":
        document = SocietyDocument.objects.get(document_id=document_id)

    elif category == "생활/문화":
        document = CultureLivingDocument.objects.get(document_id=document_id)

    elif category == "세계":
        document = WorldDocument.objects.get(document_id=document_id)

    elif category == "IT/과학":
        document = ITScienceDocument.objects.get(document_id=document_id)

    summary_document = DocumentSummary.objects.get(document_id=document_id)

    return document.title, summary_document.summary_text, document.link