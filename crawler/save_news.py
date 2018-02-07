# -*- coding: utf-8 -*-

import crawler.naver_news_crawler as cr
from article.models import *
from crawler.models import *

'''
crawler/save_news.py

'''


def save_document_id(document_id):
    doc_id = DocumentId(document_id=document_id)
    doc_id.save()


def save_document(document_id, press, category, published_date, crawled_date, title, text, link):
    if category == "정치":
        save_politics_document(document_id, press, category, published_date, crawled_date, title, text, link)
    elif category == "경제":
        save_economics_document(document_id, press, category, published_date, crawled_date, title, text, link)
    elif category == "사회":
        save_society_document(document_id, press, category, published_date, crawled_date, title, text, link)
    elif category == "생활/문화":
        save_culture_living_document(document_id, press, category, published_date, crawled_date, title, text, link)
    elif category == "세계":
        save_world_document(document_id, press, category, published_date, crawled_date, title, text, link)
    elif category == "IT/과학":
        save_it_science_document(document_id, press, category, published_date, crawled_date, title, text, link)


def save_politics_document(document_id, press, category, published_date, crawled_date, title, text, link):
    politics_document = PoliticsDocument(
            document_id=document_id,
            press=press,
            category=category,
            published_date=published_date,
            crawled_date=crawled_date,
            title=title,
            text=text,
            link=link,
    )
    politics_document.save()


def save_economics_document(document_id, press, category, published_date, crawled_date, title, text, link):
    economics_document = EconomicsDocument(
            document_id=document_id,
            press=press,
            category=category,
            published_date=published_date,
            crawled_date=crawled_date,
            title=title,
            text=text,
            link=link,
    )
    economics_document.save()


def save_society_document(document_id, press, category, published_date, crawled_date, title, text, link):
    society_document = SocietyDocument(
            document_id=document_id,
            press=press,
            category=category,
            published_date=published_date,
            crawled_date=crawled_date,
            title=title,
            text=text,
            link=link,
    )
    society_document.save()


def save_culture_living_document(document_id, press, category, published_date, crawled_date, title, text, link):
    culture_living_document = CultureLivingDocument(
            document_id=document_id,
            press=press,
            category=category,
            published_date=published_date,
            crawled_date=crawled_date,
            title=title,
            text=text,
            link=link,
    )
    culture_living_document.save()


def save_world_document(document_id, press, category, published_date, crawled_date, title, text, link):
    world_document = WorldDocument(
            document_id=document_id,
            press=press,
            category=category,
            published_date=published_date,
            crawled_date=crawled_date,
            title=title,
            text=text,
            link=link,
    )
    world_document.save()


def save_it_science_document(document_id, press, category, published_date, crawled_date, title, text, link):
    it_science_document = ITScienceDocument(
            document_id=document_id,
            press=press,
            category=category,
            published_date=published_date,
            crawled_date=crawled_date,
            title=title,
            text=text,
            link=link,
    )
    it_science_document.save()


def save_document_summary(document_id, sentences_n, text_rank, word_count, word_tfidf, summary_text):
    document_summary = DocumentSummary(
        document_id=document_id,
        sentences_n=sentences_n,
        text_rank=text_rank,
        word_count=word_count,
        word_tfidf=word_tfidf,
        summary_text=summary_text,
    )
    document_summary.save()


def save_sentiment(document_id, good, warm, sad, angry, want):
    sentiment = SentimentList(
        document_id=document_id,
        good=good,
        warm=warm,
        sad=sad,
        angry=angry,
        want=want
    )
    sentiment.save()


def save_comment(document_id, user_id, content, published_date, crawled_date, recomm, unrecomm):
    comment = Comment(
        document_id=document_id,
        user_id=user_id,
        content=content,
        published_date=published_date,
        crawled_date=crawled_date,
        recomm=recomm,
        unrecomm=unrecomm
    )
    comment.save()


def save_request(user_key, press, category, date):
    requirement = Requirement(
        user_key=user_key,
        press=press,
        category=category,
        date=date
    )
    requirement.save()


def save_crawler():
    crawler_data = CrawlerData(

    )
    crawler_data.save()


def start_crawling(crawling_time):
    print(crawling_time)
    crawler = cr.crawler(crawling_time.strftime('%Y-%m-%d'))

    date_list_len = len(crawler.date_list)

    for start in range(date_list_len):
        print("before\n", crawler.date_list)
        try:
            nd_doc_list, nd_summary_list = crawler.naver_news_crawl()

        except Exception as e:
            print("Error")

        print("after\n", crawler.date_list)

        nd_doc_len = len(nd_doc_list)
        for i in range(nd_doc_len):
            document_id = nd_doc_list[i].document_id

            if DocumentId.objects.filter(document_id=document_id).exists():
                continue

            save_document_id(document_id)

            document_id = DocumentId.objects.get(document_id=nd_doc_list[i].document_id)

            save_document(
                document_id,
                nd_doc_list[i].press,
                nd_doc_list[i].category,
                nd_doc_list[i].published_date,
                nd_doc_list[i].crawled_date,
                nd_doc_list[i].title,
                nd_doc_list[i].text,
                nd_doc_list[i].link,
            )

            save_sentiment(
                document_id,
                nd_doc_list[i].sentiment.good,
                nd_doc_list[i].sentiment.warm,
                nd_doc_list[i].sentiment.sad,
                nd_doc_list[i].sentiment.angry,
                nd_doc_list[i].sentiment.want,
            )

        nd_summary_len = len(nd_summary_list)
        for i in range(nd_summary_len):
            document_id = DocumentId.objects.get(document_id=nd_summary_list[i].document_id)

            save_document_summary(
                document_id,
                nd_summary_list[i].sentences_n,
                nd_summary_list[i].text_rank,
                nd_summary_list[i].word_count,
                nd_summary_list[i].word_tfidf,
                nd_summary_list[i].summary_text,
            )

    save_crawler()
