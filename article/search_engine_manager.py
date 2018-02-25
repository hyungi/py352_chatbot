import numpy as np
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import pairwise_distances
from konlpy.tag import Mecab
import re
from crawler.models import DocumentSummary, DocumentId


class search_engine_manager:
    def __init__(self, **path):
        '''
        page_rank를 이용해 검색 엔진 기능을 제공한다. 새로운 문서가 추가될 때마다 page_rank 관련 테이블들을 사전에 만들어두고,
        검색이 요청되면 최소한의 탐색 시간 안에 결과를 반환할 수 있도록 한다.
        :param path: document_list(각 document의 tf_vector를 원소로 갖는 list)을 저장할 path (string) 
        '''
        #path directory setting
        self.dtm_path = path["dtm_path"]
        self.matrix_path = path["matrix_path"]

        #initialize variables
        self.dtm_index = []
        self.dtm_list = []
        self.vctr = CountVectorizer()
        self.tfvtr = TfidfVectorizer()
        self.feature_names = None
        self.count_matrix = None
        self.page_rank_dictionary = None

        #dtm_index & dtm_list pickle from path directory
        try: #파일이 존재하는 경우
            with open(self.dtm_path, mode="rb") as fp:
                self.dtm_index, self.dtm_list = pickle.load(fp)

            if len(self.dtm_index) == 0: #파일이 존재하지만 저장된 정보가 없을 경우
                print("Empty Document_Term_Matrix has been loaded.")
            else: #정보가 이미 저장된 파일이 존재하는 경우
                print("Document_Term_Matrix has been loaded successfully.")

        except: #파일이 없는 경우 메세지를 띄우고 새로 빈 파일을 생성한다.
            print("There is no existing Document_Term_Matrix.")
            with open(self.dtm_path, mode="wb") as fp:
                pickle.dump([self.dtm_index, self.dtm_list], fp)
            print("New Document_Term_Matrix has been created.")

        #vctr & count_matrix pickle from path directory
        try: #파일이 존재하는 경우
            with open(self.matrix_path, mode="rb") as fp:
                self.feature_names, self.count_matrix, self.page_rank_dictionary = pickle.load(fp)

            if self.page_rank_dictionary==None: #파일이 존재하지만 저장된 정보가 없을 경우
                print("Empty Matrixes have been loaded.")
            else: #정보가 이미 저장된 파일이 존재하는 경우
                print("Matrixes have been loaded successfully.")

        except: #파일이 없는 경우 메세지를 띄우고 새로 빈 파일을 생성한다.
            print("There are no existing Matrixes.")
            with open(self.matrix_path, mode="wb") as fp:
                pickle.dump([self.feature_names, self.count_matrix, self.page_rank_dictionary], fp)
            print("New Matrixes have been created.")


    def get_document_tfvector(self, document_id):
        '''
        document_id를 받아서 해당 document의 tf-idf vector를 가져오는 함수
        :param document_id: 뉴스의 document_id (string)
        :return: 해당 document의 tf-idf vector (dictionary)
        '''
        # temp = {'기본': 0.07202824060656197, '독자': 0.03601412030328099, '스스로': 0.03601412030328099, '엇갈려': 0.03601412030328099, '라고': 0.03601412030328099, '청와대': 0.18007060151640494, '구조': 0.2160847218196859, '문재인': 0.07202824060656197, '위한': 0.03601412030328099, '공개': 0.03601412030328099, '다른': 0.03601412030328099, '바른': 0.03601412030328099, '전재': 0.03601412030328099, '절대': 0.03601412030328099, '같이': 0.03601412030328099, '지시': 0.03601412030328099, '장관': 0.03601412030328099, '관계자': 0.03601412030328099, '단독': 0.03601412030328099, '헤리티지': 0.03601412030328099, '합의': 0.03601412030328099, '미루': 0.03601412030328099, '덕분': 0.03601412030328099, '분산': 0.03601412030328099, '당은': 0.03601412030328099, '김성태': 0.03601412030328099, '대통령': 0.5402118045492148, '반드시': 0.03601412030328099, '무단': 0.03601412030328099, '이날': 0.03601412030328099, '구상': 0.03601412030328099, '직접': 0.03601412030328099, '언론': 0.03601412030328099, '입장': 0.03601412030328099, '위원장': 0.03601412030328099, '오신환': 0.03601412030328099, '동떨어진': 0.03601412030328099, '지방': 0.03601412030328099, '원칙': 0.03601412030328099, '관측': 0.03601412030328099, '지역': 0.03601412030328099, '분권': 0.14405648121312395, '회견': 0.03601412030328099, '회동': 0.03601412030328099, '선거': 0.03601412030328099, '우열': 0.03601412030328099, '제도': 0.03601412030328099, '국회': 0.03601412030328099, '측면': 0.03601412030328099, '해소': 0.03601412030328099, '만큼': 0.03601412030328099, '신년': 0.03601412030328099, '방안': 0.03601412030328099, '기자': 0.07202824060656197, '접점': 0.03601412030328099, '페이스북': 0.03601412030328099, '굳이': 0.03601412030328099, '너무나': 0.03601412030328099, '가장': 0.03601412030328099, '수준': 0.03601412030328099, '일단': 0.03601412030328099, '지적': 0.03601412030328099, '금지': 0.03601412030328099, '해결': 0.03601412030328099, '선거구': 0.10804236090984295, '비례': 0.03601412030328099, '따라': 0.03601412030328099, '저지': 0.03601412030328099, '국민': 0.14405648121312395, '얘기': 0.03601412030328099, '문제점': 0.03601412030328099, '주도': 0.10804236090984295, '지난해': 0.07202824060656197, '자치': 0.03601412030328099, '하지만': 0.07202824060656197, '원내대표': 0.14405648121312395, '정당': 0.03601412030328099, '유지': 0.14405648121312395, '자유': 0.03601412030328099, '정치': 0.07202824060656197, '한다는': 0.03601412030328099, '야당': 0.03601412030328099, '김동철': 0.03601412030328099, '개편': 0.07202824060656197, '윤곽': 0.03601412030328099, '동아일보': 0.14405648121312395, '생각': 0.18007060151640494, '분명히': 0.03601412030328099, '제외': 0.03601412030328099, '과정': 0.03601412030328099, '어려운': 0.03601412030328099, '총의': 0.03601412030328099, '인터뷰': 0.03601412030328099, '언급': 0.03601412030328099, '한다': 0.03601412030328099, '정해구': 0.03601412030328099, '나온다': 0.03601412030328099, '정부': 0.03601412030328099, '빠질': 0.03601412030328099, '편안': 0.07202824060656197, '논의': 0.03601412030328099, '된다면': 0.03601412030328099, '나중': 0.03601412030328099, '여지': 0.07202824060656197, '문제': 0.07202824060656197, '여러분': 0.03601412030328099, '개헌안': 0.2160847218196859, '선택': 0.03601412030328099, '높일': 0.03601412030328099, '남겨': 0.03601412030328099, '그대로': 0.03601412030328099, '마련': 0.07202824060656197, '지난달': 0.03601412030328099, '국당': 0.03601412030328099, '권력': 0.2881129624262479, '포함': 0.03601412030328099, '둔다': 0.03601412030328099, '소신': 0.03601412030328099, '주장': 0.07202824060656197, '핵심': 0.03601412030328099, '타파': 0.03601412030328099, '임기': 0.03601412030328099, '구도': 0.03601412030328099, '동아': 0.03601412030328099, '여야': 0.03601412030328099, '집중': 0.07202824060656197, '입니다': 0.03601412030328099, '공식': 0.03601412030328099, '모으': 0.03601412030328099, '만약': 0.03601412030328099, '대한': 0.07202824060656197, '제왕': 0.18007060151640494, '따지': 0.03601412030328099, '댄다는': 0.03601412030328099, '앞서': 0.03601412030328099, '종식': 0.07202824060656197, '나섰': 0.03601412030328099, '한국': 0.03601412030328099, '협상': 0.07202824060656197, '다수': 0.03601412030328099, '문재': 0.03601412030328099, '정책': 0.03601412030328099, '개헌': 0.2520988421229669, '배포': 0.03601412030328099, '기획': 0.03601412030328099, '관심': 0.10804236090984295, '형태': 0.03601412030328099}
        # temp는 위와 같은 꼴의 정보이다.
        # return temp

        query_result = DocumentSummary.objects.filter(
            document_id=DocumentId.objects.get(document_id=document_id)).values_list(
            'word_tfidf', flat=True)
        string1 = str(list(query_result))
        list1 = string1[3:-3].split(',')
        word_tfidf_dict = {}

        for i in list1:
            tmp_list = i.split(':')
            value1 = tmp_list[0].replace('\'', '')
            word_tfidf_dict[value1.strip(' ')] = float(tmp_list[1].strip(' '))

        return word_tfidf_dict


    def add_new_document(self, doucment_id_list):
        '''
        document_id들을 인자로 받아서 해당 document_id의 tf_vector들을 파일에 추가하고, jaccard_similarity_matrix를 업데이트한다.
        :param doucment_id_list: document_id를 원소로 갖는 리스트 (list) 
        :return: None
        '''
        for document_id in doucment_id_list:
            if document_id not in self.dtm_index:
                tf_dic = self.get_document_tfvector(document_id)
                tf_list = [(k, v) for k, v in tf_dic.items() if v > 0.1]  # tfidf 값이 0.1 이상인 정보만 남긴다.
                tf_list = sorted(tf_list, key=lambda word: word[1], reverse=True)  # 내림차순으로 정렬
                tf_list = [x[0] for x in tf_list][:10]  # 상위 10개
                tf_string = " ".join(tf_list)

                self.dtm_index.append(document_id)
                self.dtm_list.append(tf_string)
            else:
                print("The document_id", document_id, "is already included in dtm_list.")

        self.save_updated_document_list()
        self.save_updated_matrix()


    def save_updated_document_list(self):
        '''
        문서가 추가될 때마다 dtm_index와 dtm_list를 추가하여 업데이트한다.
        :return: None
        '''
        with open(self.dtm_path, mode="wb") as fp:
            pickle.dump([self.dtm_index, self.dtm_list], fp)


    def save_updated_matrix(self):
        '''
        문서가 추가될 때마다 count_matrix와 feature_names, page_rank_dictionary를 추가하여 업데이트한다.
        :return: 
        '''
        self.count_matrix = self.vctr.fit_transform(self.dtm_list).toarray()
        self.feature_names = self.vctr.get_feature_names()

        tfidf_matrix = self.tfvtr.fit_transform(self.dtm_list).toarray()
        tfidf_mat = np.asarray(tfidf_matrix)
        d = 0.85  # d = damping factor, the ratio of moving to pages following link
        tfidf_graph = np.dot(tfidf_mat, tfidf_mat.T)
        matrix_size = tfidf_graph.shape[0]

        for id in range(matrix_size):
            tfidf_graph[id, id] = 0  # diagonal 부분을 0으로
            link_sum = np.sum(tfidf_graph[:, id])  # A[:, id] = A[:][id]
            if link_sum != 0:
                tfidf_graph[:, id] /= link_sum
            tfidf_graph[:, id] *= -d
            tfidf_graph[id, id] = 1

        B = (1 - d) * np.ones((matrix_size, 1))
        ranks = np.linalg.solve(tfidf_graph, B)  # 연립방정식 Ax = b
        textrank_dictionary = {idx: r[0] for idx, r in zip(self.dtm_index, ranks)}
        self.page_rank_dictionary = textrank_dictionary

        with open(self.matrix_path, mode="wb") as fp:
            pickle.dump([self.feature_names, self.count_matrix, self.page_rank_dictionary], fp)


    def stemming_user_query(self, search_query):
        remove_pos = "[(?P<조사>JK.*)(?P<접속조사>JC.*)(?P<전성어미>ET.*)(?P<종결어미>EF.*)(?P<연결어미>EC.*)(?P<접미사>XS.*)(?P<마침표물음표느낌표>SF.*)(?P<쉼표가운뎃점콜론빗금>SC.*)]"  # mecab
        mecab = Mecab()
        stemmed_words = mecab.pos(search_query)
        stemmed_words = [x[0] for x in stemmed_words if not bool(re.match(remove_pos, x[1]))]

        return ' '.join(stemmed_words)


    def search_news_document(self, search_query, n=5):
        '''
        검색어가 포함된 document 중 가장 가까운 높은 page_rank value의 상위 n개 document를 원소로 갖는 리스트를 반환한다.
        :param search_query: 찾고자 하는 검색어 (string)
        :param n: 유사한 document의 수 (integer) #보통 n=5 정도로 하자. 
        :return: 검색어와 가장 유사한 document_id를 원소로 갖는 리스트 (list)
        '''

        user_query = self.stemming_user_query(search_query)

        col_index = []
        for query in user_query.split():
            if query in self.feature_names:
                col_index.append(self.feature_names.index(query))

        target_columns = self.count_matrix[:, col_index]
        target_document_id = np.array(self.dtm_index)[np.sum(target_columns, axis=1) != 0]

        target_dictionary = {k: v for k, v in self.page_rank_dictionary.items() if k in target_document_id}
        sorted_target_dictionary = sorted(target_dictionary, key=lambda k: target_dictionary[k], reverse=True)[0:n]

        return sorted_target_dictionary
