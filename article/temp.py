#-*-coding:utf-8-*
import pickle
import numpy as np
import pandas as pd
from math import pi

import nltk

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib import rc
import pytagcloud
import pygame
from crawler.models import DocumentSummary, DocumentId
from article.models import UserStatus, NewsRecord


class user_analysis_visualization:
    def __init__(self, path):
        self.path = path

        self.user_info = ""
        with open(path, mode="rb") as fp:
            self.user_info = pickle.load(fp)

        self.col_names = self.user_info.columns.values

        self.category_index = ["정치", "경제", "사회", "생활/문화", "세계", "IT/과학"]
        self.press_index = [name for name in self.col_names if name not in self.category_index]


    def get_document_tfvector(self, document_id):
        '''
        document_id를 받아서 해당 document의 tf-idf vector를 가져오는 함수
        :param document_id: 뉴스의 document_id (string)
        :return: 해당 document의 tf-idf vector (dictionary)
        '''
        query_result = DocumentSummary.objects.filter(
                                                      document_id=DocumentId.objects.get(document_id=document_id)).values_list('word_tfidf', flat=True)
        string1 = str(list(query_result))
        list1 = string1[3:-3].split(',')
        word_tfidf_dict = {}
                                                                                                                               
        for i in list1:
            tmp_list = i.split(':')
            value1 = tmp_list[0].replace('\'', '')
            word_tfidf_dict[value1.strip(' ')] = float(tmp_list[1].strip(' '))
                                                                                                                               
        return word_tfidf_dict

    def get_document_id_list(self):
        #self.user_key에 해당하는 user의 최근 1주일치 document_id_list 반환
        user_status_instance = UserStatus.objects.get(user_key=self.user_key)
        news_record_instance = NewsRecord.objects.filter(user_status=user_status_instance).order_by('-request_time').values_list('request_news_id',flat=True)[:20]
        
        return list(news_record_instance)


    def user_setting(self, user_key):
        self.user_key = user_key

        # category vairables preprocessing
        self.user_category_index = self.category_index
        self.ct_N = len(self.user_category_index)
        self.category_angle = [n / float(self.ct_N) * 2 * pi for n in range(self.ct_N)]
        self.category_angle += self.category_angle[:1]

        self.category_value = []
        for ct in self.user_category_index:
            self.category_value.append(self.user_info.loc[self.user_key].loc[ct])
        self.category_value = self.category_value + self.category_value[0:1]
        self.scaled_category_value = np.round(self.category_value / sum(self.category_value), 4) * 100
        self.category_value_max = np.ceil(max(self.scaled_category_value) / 10) * 10

        # press vairables preprocessing
        press_dic = dict()
        for pr in self.press_index:
            press_dic[pr] = (self.user_info.loc[self.user_key].loc[pr])
        press_dic_sorted = sorted(press_dic, key=lambda k: press_dic[k], reverse=True)
        self.user_press_index = press_dic_sorted[0:6]

        self.press_value = []
        for pr in self.user_press_index:
            self.press_value.append(press_dic[pr])

        self.pr_N = len(self.user_press_index)
        self.press_angle = [n / float(self.pr_N) * 2 * pi for n in range(self.pr_N)]
        self.press_angle += self.press_angle[:1]
        self.press_value = self.press_value + self.press_value[0:1]

        self.scaled_press_value = np.round(self.press_value / sum(self.press_value), 4) * 100
        self.press_value_max = np.ceil(max(self.scaled_press_value) / 10) * 10

        document_id_list = self.get_document_id_list()
        self.user_corpus = []
        for document_id in document_id_list:
            tf_dic = self.get_document_tfvector(document_id)
            tf_list = [(k, v) for k, v in tf_dic.items() if v > 0.1]  # tfidf 값이 0.1 이상인 정보만 남긴다.
            tf_list = sorted(tf_list, key=lambda word: word[1], reverse=True)  # 내림차순으로 정렬
            tf_list = [x[0] for x in tf_list][:10]  # 상위 10개
            tf_string = " ".join(tf_list)
            self.user_corpus.append(tf_string)


    def create_spider_chart(self):
        rc('font', family="NanumBarunGothicOTF")
        plt.rcParams["font.family"]

        plt.figure(figsize=[20, 10])

        ax = plt.subplot(221, polar=True)
        plt.title("뉴스 카테고리 분석", size=25)
        plt.xticks(self.category_angle[:-1], self.user_category_index, color='grey', size=20)
        ax.set_rlabel_position(0)
        plt.yticks([self.category_value_max * 0.25, self.category_value_max * 0.5, self.category_value_max * 0.75],
                   ["25%", "50%", "75%"], color="grey", size=15)
        plt.ylim(0, self.category_value_max)
        ax.plot(self.category_angle, self.scaled_category_value, linewidth=1, linestyle='solid')
        ax.fill(self.category_angle, self.scaled_category_value, 'b', alpha=0.1)

        ax = plt.subplot(222, polar=True)
        plt.title("신문사 경향성 분석", size=25)
        plt.xticks(self.press_angle[:-1], self.user_press_index, color='grey', size=20)
        ax.set_rlabel_position(0)
        plt.yticks([self.press_value_max * 0.25, self.press_value_max * 0.5, self.press_value_max * 0.75],
                   ["25%", "50%", "75%"], color="grey", size=15)
        plt.ylim(0, self.press_value_max)
        ax.plot(self.press_angle, self.scaled_press_value, linewidth=1, linestyle='solid')
        ax.fill(self.press_angle, self.scaled_press_value, 'b', alpha=0.1)

        plt.tight_layout()
        plt.subplots_adjust(wspace=-0.4)
        # plt.show()
        plt.savefig('user_spider_chart.png', dpi=100)
        plt.close()


    def create_wordcloud(self):
        user_word_token = [word for sentence in self.user_corpus for word in sentence.split()]
        text = "문재인 대통령 방한 미국 짱짱맨 오늘 트럼프 트위터 개웃겨 문재인 대통령 방한 미국 짱짱맨 오늘 트럼프 트위터 개웃겨 문재인 대통령 방한 미국 짱짱맨 오늘 트럼프 트위터 개웃겨"
        user_word_token = text.split(" ")
        user_word_token = nltk.Text(user_word_token, name="user_wordcloud")
        user_word_data = user_word_token.vocab().most_common(50)
        user_tag_list = pytagcloud.make_tags(user_word_data, maxsize=80)
        pytagcloud.create_tag_image(user_tag_list, 'user_wordcloud.png', size=(1000, 500), fontname='Korean', rectangular=False)


    def save_integrated_img(self):
        img1 = mpimg.imread('user_spider_chart.png')
        img2 = mpimg.imread('user_wordcloud.png')

        fig = plt.figure(figsize=(15, 15))
        fig.add_subplot(2, 1, 1)
        plt.imshow(img1)
        plt.axis("off")

        fig.add_subplot(2, 1, 2)
        plt.imshow(img2)
        plt.axis("off")

        plt.tight_layout()
        fig.subplots_adjust(hspace=-0.4)
        plt.savefig('user_analysis_image.png', dpi=100)


    def printcheck(self):
        print("category:")
        print(self.user_category_index)
        print(self.scaled_category_value)
        print(self.category_angle)
        print("\npress")
        print(self.user_press_index)
        print(self.scaled_press_value)
        print(self.press_angle)



