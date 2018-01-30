# -*- coding: utf-8 -*-

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
import django
django.setup()

from django.http import HttpResponseNotFound
from django.utils import timezone
import crawler.naver_news_crawler as cr
from article.models import *
from crawler.models import *




'''
crawler/saveNews.py
 
# Feedback 객체 생성
fb = Feedback(name = 'Kim', email = 'kim@test.com', comment='Hi', createDate=datetime.now())
 
# 새 객체 INSERT
fb.save()


'''
def saveDocument(idid, ipress, icategory, ipd, icd, ititle, itext, ilink):
    '''
    각각의 데이터에 대응하는 input 데이터의 목록
    :param idid:
    :param ipress:
    :param icategory:
    :param ipd:
    :param icd:
    :param ititle:
    :param itext:
    :param ilink:
    :return: 없음. DB에 .save() 를 통해 저장
    '''

    doc = Document(
            document_id=idid,
            press=ipress,
            category=icategory,
            published_date=ipd,
            crawled_date=icd,
            title=ititle,
            text=itext,
            link=ilink,
    )
    doc.save()


def saveDocSummary(idid, is_n, it_rank, itwc, itwt, ist):
    docSum = DocumentSummary(
        document_id=idid,
        sentences_n=is_n,
        text_rank=it_rank,
        word_count=itwc,
        word_tfidf=itwt,
        summary_text=ist,
    )
    docSum.save()


def saveSentiment(idid, igood, iwarm, isad, iangry, iwant):
    sentiment = SentimentList(
        document_id=idid,
        good=igood,
        warm=iwarm,
        sad=isad,
        angry=iangry,
        want=iwant
    )
    sentiment.save()


def saveComment(idid, iuid, icontent, ipd, icd, irecomm, iunrecomm):
    comment = Comment(
        document_id=idid,
        user_id=iuid,
        content=icontent,
        published_date=ipd,
        crawled_date=icd,
        recomm=irecomm,
        unrecomm=iunrecomm
    )
    comment.save()


def saveReq(iuser_key, ipress, icategory, idate):
    requirement = Requirement(
        user_key=iuser_key,
        press=ipress,
        category=icategory,
        date=idate
    )
    requirement.save()


def save_crawler():
    crawler_data = CrawlerData(
        crawler_data=timezone.now()
    )
    crawler_data.save()


def start_crawling():
    cur_time = timezone.now().strftime('%Y-%m-%d')
    # cur_time = "2018-01-04"
    # print(cur_time)
    crawler = cr.crawler(cur_time)

    date_list_len = len(crawler.date_list)

    for start in range(date_list_len):
        print("before\n", crawler.date_list)
        nd_doc_list, nd_summary_list = crawler.naver_news_crawl()

        # nd_doc_list, nd_summary_list, nd_comment_dict = crawler.naver_news_crawl()
        print("after\n", crawler.date_list)

        nd_doc_len = len(nd_doc_list)
        for i in range(nd_doc_len):
            saveDocument(
                nd_doc_list[i].document_id,
                nd_doc_list[i].press,
                nd_doc_list[i].category,
                nd_doc_list[i].published_date,
                nd_doc_list[i].crawled_date,
                nd_doc_list[i].title,
                nd_doc_list[i].text,
                nd_doc_list[i].link,

            )

            doc_id = Document.objects.get(document_id=nd_doc_list[i].document_id)
            saveSentiment(
                doc_id,
                nd_doc_list[i].sentiment.good,
                nd_doc_list[i].sentiment.warm,
                nd_doc_list[i].sentiment.sad,
                nd_doc_list[i].sentiment.angry,
                nd_doc_list[i].sentiment.want,
            )

        '''
            comment_dict_len = len(nd_comment_dict[nd_doc_list[i].document_id])
            comment_dict_list = nd_comment_dict[nd_doc_list[i].document_id]

            for j in range(comment_dict_len):

                saveComment(
                    doc_id,
                    comment_dict_list[j].user_id,
                    comment_dict_list[j].content,
                    comment_dict_list[j].published_date,
                    comment_dict_list[j].crawled_date,
                    comment_dict_list[j].recomm,
                    comment_dict_list[j].unrecomm,
                )
        '''
        nd_summary_len = len(nd_summary_list)
        for i in range(nd_summary_len):
            doc_id = Document.objects.get(document_id=nd_summary_list[i].document_id)

            saveDocSummary(
                doc_id,
                nd_summary_list[i].sentences_n,
                nd_summary_list[i].text_rank,
                nd_summary_list[i].word_count,
                nd_summary_list[i].word_tfidf,
                nd_summary_list[i].summary_text,
            )

    save_crawler()


start_crawling()
