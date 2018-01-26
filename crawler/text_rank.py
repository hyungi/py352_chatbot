# -*- coding: utf-8 -*-
from konlpy.tag import Kkma
from konlpy.tag import Mecab
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from . import news_document_class as nd
import numpy as np
import re

'''
주어진 문서를 n줄로 요약하는 메소드인 get_n_summary와 문서에서 tfidf[count] vector[matrix]를 구하는 메소드 선언
'''


class text_rank:
    def __init__(self, text):
        self.text = nd.prettify_sentences(text)
        self.sentences_n = len(text.split("."))
        self.summary_n = None

    def select_summary_n(self):
        sentence_n = 10
        n_class = [(3, range(0, 11)),
                   (4, range(11, 21)),
                   (5, range(21, 31)),
                   (6, range(31, 41)),
                   (7, range(41, 51)),
                   (8, range(51, 101))]
        for x in n_class:
            if self.sentences_n in x[1]:
                self.summary_n = x[0]
                break

    def doc_to_stemmed_words(self) :
        '''
        뉴스기사의 각 문장에서 추출한 단어의 어근들을 반환한다.
        :param text: 뉴스기사 텍스트 (string) 
        :return: 각 문장에서 추출한 단어의 어근들의 리스트를 원소로 갖는 리스트 (nested list)
        '''

        sentences = (self.text).split(".")

        # kkma = Kkma()
        # remove_pos = "[(?P<조사>JK.*)(?P<접속조사>JC.*)(?P<전성어미>ET.*)(?P<종결어미>EF.*)(?P<연결어미>EC.*)(?P<접미사>XS.*)(?P<마침표물음표느낌표>SF.*)(?P<쉼표가운뎃점콜론빗금>SP.*)]" #kkma
        mecab = Mecab()
        remove_pos = "[(?P<조사>JK.*)(?P<접속조사>JC.*)(?P<전성어미>ET.*)(?P<종결어미>EF.*)(?P<연결어미>EC.*)(?P<접미사>XS.*)(?P<마침표물음표느낌표>SF.*)(?P<쉼표가운뎃점콜론빗금>SC.*)]"  # mecab

        stemmed_sentences = []

        for sentence in sentences:
            # stemmed_words = kkma.pos(sentence)
            stemmed_words = mecab.pos(sentence)
            stemmed_words = [x[0] for x in stemmed_words if not bool(re.match(remove_pos, x[1]))]
            stemmed_sentences.append(stemmed_words)

        return stemmed_sentences

    def get_tfidf_vector(self):
        '''
        어근 추출된 뉴스 기사의 단어 벡터와 그 단어들의 tfidf 값을 원소로 갖는 벡터를 반환한다. 
        :param text: 뉴스기사 텍스트 (string)
        :return: tfidf를 구한 어근을 원소로 갖는 리스트 (list), tfidf 값을 원소로 갖는 리스트 (list) 
        '''

        stemmed_sentences = self.doc_to_stemmed_words()
        remove_pattern = re.compile('[^ ㄱ-ㅣ가-힣0-9a-zA-Z]+')  # 한글,숫자,영어 제외한 문자

        tfidf = TfidfVectorizer()

        stemmed_article = []
        for stemmed_words in stemmed_sentences :
            sentence = " ".join(stemmed_words)  # stemmed된 단어를 사용할 예정
            sentence = remove_pattern.sub("", sentence)  # 한글, 숫자 제외한 문자는 제거 #본래 문장을 보여줄 땐 필요하지만 vector map 작성엔 불필요
            stemmed_article.append(sentence)

        stemmed_article = [" ".join(stemmed_article)]
        tfidf_vec = np.ndarray.tolist(np.squeeze(tfidf.fit_transform(stemmed_article).toarray()))
        feature_name = tfidf.get_feature_names()

        return feature_name, tfidf_vec

    def get_tfidf_matrix(self) :
        '''
        어근 추출된 뉴스 기사의 각 문장의 단어 리스트와 그 단어들의 tfidf 값을 원소로 갖는 행렬을 반환한다.
        :param text: 뉴스기사 텍스트 (string)
        :return: tfidf를 구한 어근을 원소로 갖는 리스트 (list), tfidf 값을 원소로 갖는 이중 리스트 (nested list) 
        '''
        stemmed_sentences = self.doc_to_stemmed_words()
        remove_pattern = re.compile('[^ ㄱ-ㅣ가-힣0-9a-zA-Z]+')  # 한글,숫자,영어 제외한 문자

        tfidf = TfidfVectorizer()

        stemmed_article = []
        for stemmed_words in stemmed_sentences :
            sentence = " ".join(stemmed_words)  # stemmed된 단어를 사용할 예정
            sentence = remove_pattern.sub("", sentence)  # 한글, 숫자 제외한 문자는 제거 #본래 문장을 보여줄 땐 필요하지만 vector map 작성엔 불필요
            stemmed_article.append(sentence)

        tfidf_mat = tfidf.fit_transform(stemmed_article).toarray()
        feature_name = tfidf.get_feature_names()

        return feature_name, tfidf_mat

    def get_count_vector(self) :
        '''
        어근 추출된 뉴스 기사의 단어 벡터와 그 단어들의 count값을 원소로 갖는 벡터를 반환한다. 
        :param text: 뉴스기사 텍스트 (string)
        :return: count를 구한 어근을 원소로 갖는 리스트 (list), count값을 원소로 갖는 리스트 (list) 
        '''
        stemmed_sentences = self.doc_to_stemmed_words()
        remove_pattern = re.compile('[^ ㄱ-ㅣ가-힣0-9a-zA-Z]+')  # 한글,숫자,영어 제외한 문자

        cnt_vec = CountVectorizer()

        stemmed_article = []
        for stemmed_words in stemmed_sentences :
            sentence = " ".join(stemmed_words)  # stemmed된 단어를 사용할 예정
            sentence = remove_pattern.sub("", sentence)  # 한글, 숫자 제외한 문자는 제거 #본래 문장을 보여줄 땐 필요하지만 vector map 작성엔 불필요
            stemmed_article.append(sentence)

        stemmed_article = [" ".join(stemmed_article)]
        count_vec = np.ndarray.tolist(np.squeeze(cnt_vec.fit_transform(stemmed_article).toarray()))
        feature_name = cnt_vec.get_feature_names()

        return feature_name, count_vec

    def get_count_matrix(self):
        '''
        어근 추출된 뉴스 기사의 단어 벡터와 그 단어들의 count 값을 원소로 갖는 행렬을 반환한다. 
        :param text: 뉴스기사 텍스트 (string)
        :return: count를 구한 어근을 원소로 갖는 리스트 (list), count 값을 원소로 갖는 이중 리스트 (nested list) 
        '''
        stemmed_sentences = self.doc_to_stemmed_words()
        remove_pattern = re.compile('[^ ㄱ-ㅣ가-힣0-9a-zA-Z]+')  # 한글,숫자,영어 제외한 문자

        cnt_vec = CountVectorizer()

        stemmed_article = []
        for stemmed_words in stemmed_sentences :
            sentence = " ".join(stemmed_words)  # stemmed된 단어를 사용할 예정
            sentence = remove_pattern.sub("", sentence)  # 한글, 숫자 제외한 문자는 제거 #본래 문장을 보여줄 땐 필요하지만 vector map 작성엔 불필요
            stemmed_article.append(sentence)

        count_vec = np.ndarray.tolist(np.squeeze(cnt_vec.fit_transform(stemmed_article).toarray()))
        feature_name = cnt_vec.get_feature_names()

        return feature_name, count_vec

    def get_textrank_from_text(self):
        '''
        문장들의 tfidf 행렬을 이용해 각 문장들 간의 text rank graph를 구하고, 각 문장의 text rank 값을 계산한다.
        각 문장 번호와 textrank 값을 사전 형태로 반환한다.
        :param text: 뉴스기사 텍스트 (string)
        :param n: 요약하고자 하는 줄 수 (integer)
        :return: 문장의 index, text rank를 각각 key/value로 갖는 사전 (dictionary)
        '''
        _, tfidf_mat = self.get_tfidf_matrix()
        tfidf_mat = np.asarray(tfidf_mat)

        d = 0.85  # d = damping factor
        tfidf_graph = np.dot(tfidf_mat, tfidf_mat.T)
        matrix_size = tfidf_graph.shape[0]

        for id in range(matrix_size):
            tfidf_graph[id, id] = 0  # diagonal 부분을 0으로
            link_sum = np.sum(tfidf_graph[:, id])  # A[:, id] = A[:][id]
            if link_sum != 0:
                tfidf_graph[:, id] /= link_sum
            tfidf_graph[:, id] *= -d
            tfidf_graph[id, id] = 1

        B = (1-d) * np.ones((matrix_size, 1))
        ranks = np.linalg.solve(tfidf_graph, B)  # 연립방정식 Ax = b
        textrank_dictionary = {idx: r[0] for idx, r in enumerate(ranks)}

        return textrank_dictionary

    def get_summary(self):
        '''
        반환된 index를 바탕으로 전체 뉴스 기사 중 가장 중요도 높은 문장을 순서대로 n개 저장한 리스트를 반환한다.
        :param text: 뉴스기사 텍스트 (string)
        :param n: 요약하고자 하는 줄 수 (integer) 
        :return: top n개의 문장을 원소로 갖는 리스트 (list)
        '''
        self.select_summary_n()
        n = self.summary_n
        article = [x+"." for x in (self.text).split(".")]
        textrank_dictionary = self.get_textrank_from_text()
        sorted_textrank = sorted(textrank_dictionary, key=lambda k: textrank_dictionary[k], reverse=True)[0:n]
        sorted_textrank.sort()

        summary = []
        for idx in sorted_textrank :
            summary.append(article[idx])

        return summary
