# -*- coding: utf-8 -*-

from .models import *

'''
/crawler/get_news.py

'''

all_doc = []

pol_doc = PoliticsDocument.objects.all().values_list(
    'published_date', 'title', 'document_id',
).order_by('-published_date')

eco_doc = EconomicsDocument.objects.all().values_list(
    'published_date', 'title', 'document_id',
).order_by('-published_date')

soc_doc = SocietyDocument.objects.all().values_list(
    'published_date', 'title', 'document_id',
).order_by('-published_date')

cul_doc = CultureLivingDocument.objects.all().values_list(
    'published_date', 'title', 'document_id',
).order_by('-published_date')

wol_doc = WorldDocument.objects.all().values_list(
    'published_date', 'title', 'document_id',
).order_by('-published_date')

it_doc = ITScienceDocument.objects.all().values_list(
    'published_date', 'title', 'document_id',
).order_by('-published_date')

all_doc += list(pol_doc)
all_doc += list(eco_doc)
all_doc += list(soc_doc)
all_doc += list(cul_doc)
all_doc += list(wol_doc)
all_doc += list(it_doc)
all_doc.sort(reverse=True)

print('latest_news_set is loaded')


def get_news(press, date, category):
    year = int(date[0:4])
    month = int(date[5:7])
    day = int(date[8:10])

    """
    :params
    고객이 입력한 press, year, month, day, category 정보를 바탕으로
    이에 맞는 뉴스 정보를 되돌려주는 함수(최신 10개 기사)
    :returns
    쿼리문에 의해 골라진 쿼리셋을
    response = {'key':'value'}  value = title / key = document_id
    위와 같은 형태로 저장하여 전송한다.
    """

    if category == "정치":
        document = PoliticsDocument.objects.filter(press=press)
        document = document.filter(published_date__year=year)
        document = document.filter(published_date__month=month)
        document = document.filter(published_date__day=day).order_by("-published_date")

    elif category == "경제":
        document = EconomicsDocument.objects.filter(press=press)
        document = document.filter(published_date__year=year)
        document = document.filter(published_date__month=month)
        document = document.filter(published_date__day=day).order_by("-published_date")

    elif category == "사회":
        document = SocietyDocument.objects.filter(press=press)
        document = document.filter(published_date__year=year)
        document = document.filter(published_date__month=month)
        document = document.filter(published_date__day=day).order_by("-published_date")

    elif category == "생활/문화":
        document = CultureLivingDocument.objects.filter(press=press)
        document = document.filter(published_date__year=year)
        document = document.filter(published_date__month=month)
        document = document.filter(published_date__day=day).order_by("-published_date")

    elif category == "세계":
        document = WorldDocument.objects.filter(press=press)
        document = document.filter(published_date__year=year)
        document = document.filter(published_date__month=month)
        document = document.filter(published_date__day=day).order_by("-published_date")

    elif category == "IT/과학":
        document = ITScienceDocument.objects.filter(press=press)
        document = document.filter(published_date__year=year)
        document = document.filter(published_date__month=month)
        document = document.filter(published_date__day=day).order_by("-published_date")

    print(document.values_list('published_date'))
    return_document = document.values('document_id', 'title')
    document_list = list(return_document)
    doc_list_len = len(document_list)

    response = {}

    if doc_list_len == 0:
        print("선택한 뉴스가 없습니다.")
        response["none"] = "선택한 뉴스가 없습니다."

    for i in reversed(range(doc_list_len)):
        response[document_list[i]['title']] = document_list[i]['document_id']

    return response


def get_news_by_id(document_id_list):
    list_len = len(document_id_list)
    return_dict = {}
    # print(list_len)
    for i in range(list_len):
        # print(i)
        # print(document_id_list[i])

        document = (PoliticsDocument.objects.filter(document_id=document_id_list[i]).values('document_id', 'title'))
        if len(document) > 0:
            document = list(document)
            return_dict[document[0]['title']] = document[0]['document_id']

        document = (EconomicsDocument.objects.filter(document_id=document_id_list[i]).values('document_id', 'title'))
        if len(document) != 0:
            document = list(document)
            return_dict[document[0]['title']] = document[0]['document_id']

        document = (SocietyDocument.objects.filter(document_id=document_id_list[i]).values('document_id', 'title'))
        if len(document) != 0:
            document = list(document)
            return_dict[document[0]['title']] = document[0]['document_id']

        document = (CultureLivingDocument.objects.filter(document_id=document_id_list[i]).values('document_id', 'title'))
        if len(document) != 0:
            document = list(document)
            return_dict[document[0]['title']] = document[0]['document_id']

        document = (WorldDocument.objects.filter(document_id=document_id_list[i]).values('document_id', 'title'))
        if len(document) != 0:
            document = list(document)
            return_dict[document[0]['title']] = document[0]['document_id']

        document = (ITScienceDocument.objects.filter(document_id=document_id_list[i]).values('document_id', 'title'))
        if len(document) != 0:
            document = list(document)
            return_dict[document[0]['title']] = document[0]['document_id']

    return return_dict


def get_summary(input_document_id, category):
    print(input_document_id)
    print(category)
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

    joined_summary_text = "".join(list(summary_document.summary_text))

    return document.title, joined_summary_text, document.link, document.published_date


def get_category_by_doc_id(input_document_id):
    print(input_document_id)
    if len(PoliticsDocument.objects.filter(document_id=input_document_id)) != 0:
        return '정치'
    elif len(EconomicsDocument.objects.filter(document_id=input_document_id)) != 0:
        return '경제'
    elif len(SocietyDocument.objects.filter(document_id=input_document_id)) != 0:
        return '사회'
    elif len(CultureLivingDocument.objects.filter(document_id=input_document_id)) != 0:
        return '생활/문화'
    elif len(WorldDocument.objects.filter(document_id=input_document_id)) != 0:
        return '세계'
    elif len(ITScienceDocument.objects.filter(document_id=input_document_id)) != 0:
        return 'IT/과학'


def get_press_by_doc_id_category(document_id, category):

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

    return document.press


def get_latest_news(from_number, to_number):
    global all_doc
    return_dict = {}
    return_list = []

    for i in range(from_number, to_number):
        return_dict[all_doc[i][1]] = all_doc[i][2]
        return_list += [all_doc[i][1]]

    return return_dict, return_list


def get_latest_news_id_list(from_number, to_number):
    global all_doc
    return_list = []

    for i in range(from_number, to_number):
        return_list += [all_doc[i][2]]

    return return_list
