import numpy as np
import math as m
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import collections
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
        # path directory setting
        self.docu_info_path = path["docu_info_path"]
        self.division_path = path["division_path"]
        self.batch_size = 2000

        # initialize variables
        # 공통 유지할 부분
        self.docu_info_dic = collections.OrderedDict()
        self.docu_index_list = []
        self.docu_id_list = []
        self.docu_string_list = []

        # dtm_index & dtm_list pickle from path directory
        try:  # 파일이 존재하는 경우
            with open(self.docu_info_path + ".txt", mode="rb") as fp:
                self.docu_info_dic = pickle.load(fp)

            if len(self.docu_info_dic) == 0:  # 파일이 존재하지만 저장된 정보가 없을 경우
                print("Empty Document_info file has been loaded.")
            else:  # 정보가 이미 저장된 파일이 존재하는 경우
                self.docu_index_list = list(np.array(list(self.docu_info_dic.keys())))
                self.docu_id_list = list(np.array(list(self.docu_info_dic.values()))[:, 0])
                self.docu_string_list = list(np.array(list(self.docu_info_dic.values()))[:, 1])
                print("Document_info file has been loaded successfully.")

        except:  # 파일이 없는 경우 메세지를 띄우고 새로 빈 파일을 생성한다.
            print("There is no existing Document_info file.")
            with open(self.docu_info_path + ".txt", mode="wb") as fp:
                pickle.dump(self.docu_info_dic, fp)
            print("New Document_info file has been created.")

        pointer = len(self.docu_info_dic)

        if pointer%self.batch_size == 0 and pointer/self.batch_size == 0 :
            file_index = int(m.floor(pointer / self.batch_size))
        else :
            file_index = int(m.floor(pointer / self.batch_size)) + 1

        #self.check_id_list = []
        self.file_index = file_index
        if len(self.docu_info_dic) != 0 :
            print("Start to check division file...")
            if self.check_division(self.file_index) :
                print("Division files are maintained and loaded successfully.")
            else :
                print("Check Error.")


    def check_division(self, file_index):
        if file_index <= 0 : return True

        file_dir = self.division_path + "_" + str(file_index) + ".txt"
        temp_max_range = min(file_index*self.batch_size, len(self.docu_info_dic))
        temp = [self.docu_info_dic[i] for i in range(((file_index - 1)*self.batch_size), temp_max_range)]

        if len(temp) == 0 : return True
        temp_docu_id_list = list(np.array(temp)[:,0])
        temp_docu_string_list = list(np.array(temp)[:,1])

        try :
            with open(file_dir, mode="rb") as fp :
                _, _, _, _, temp_page_rank_dic = pickle.load(fp)

            if len(temp_page_rank_dic) == len(temp_docu_id_list) :
                return True
            else :
                print("file_index:", file_index, "\tlength compare error.")
                print("temp_fn len:", len(temp_feature_name), "\ttemp_dil len:", len(temp_docu_id_list))
                print("docu_info_dic len:", len(self.docu_info_dic),"\tstart v:",((file_index - 1)*self.batch_size), "\ttemp_mr:", temp_max_range)
                return False
        except :
            #self.check_id_list = self.check_id_list + temp_docu_id_list
            if self.check_division(file_index - 1) :
                temp_feature_name, temp_count_matrix, temp_page_rank_dic = self.get_matrix_info(temp_docu_id_list, temp_docu_string_list)
                temp_set = [temp_docu_id_list, temp_docu_string_list, temp_feature_name, temp_count_matrix, temp_page_rank_dic]

                with open(file_dir, mode="wb") as fp:
                    pickle.dump(temp_set, fp)

                return True
            else :
                print("file_index:",file_index, "\tdivision dfs error.")
                return False

    def get_document_tfstring(self, document_id):
        '''
        document_id를 받아서 해당 document의 tf-idf vector를 가져오는 함수
        :param document_id: 뉴스의 document_id (string)
        :return: 해당 document의 tf-idf vector (dictionary)
        '''
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

        tf_list = [(k, v) for k, v in word_tfidf_dict.items() if v > 0.1]  # tfidf 값이 0.1 이상인 정보만 남긴다.
        tf_list = sorted(tf_list, key=lambda word: word[1], reverse=True)  # 내림차순으로 정렬
        tf_list = [x[0] for x in tf_list][:10]  # 상위 10개
        tf_string = " ".join(tf_list)

        return tf_string

    def add_new_document(self, document_id_list):
        '''
        document_id들을 인자로 받아서 해당 document_id의 tf_vector들을 파일에 추가하고, jaccard_similarity_matrix를 업데이트한다.
        :param doucment_id_list: document_id를 원소로 갖는 리스트 (list)
        :return: None
        '''

        pointer = len(self.docu_info_dic)
        if pointer%self.batch_size == 0 and pointer/self.batch_size != 0 :
            file_index = int(m.floor(pointer / self.batch_size))
        else :
            file_index = int(m.floor(pointer / self.batch_size)) + 1

        temp_docu_id_list = []
        temp_docu_string_list = []
        temp_feature_name = None
        temp_count_matrix = None
        temp_page_rank_dic = None

        if pointer % self.batch_size > 0:
            temp_docu_id_list = self.docu_id_list[self.batch_size * (file_index - 1):len(self.docu_id_list)]
            temp_docu_string_list = self.docu_string_list[self.batch_size * (file_index - 1):len(self.docu_id_list)]

        for document_id in document_id_list:
            if document_id in self.docu_id_list: continue
            temp_string = self.get_document_tfstring(document_id)

            self.docu_info_dic[pointer] = [document_id, temp_string]
            self.docu_index_list.append(pointer)
            self.docu_id_list.append(document_id)
            self.docu_string_list.append(temp_string)

            temp_docu_id_list.append(document_id)
            temp_docu_string_list.append(temp_string)
            pointer += 1

            if (len(self.docu_info_dic)) % self.batch_size == 0:
                file_dir = self.division_path + "_" + str(file_index) + ".txt"
                temp_feature_name, temp_count_matrix, temp_page_rank_dic = self.get_matrix_info(temp_docu_id_list,
                                                                                                temp_docu_string_list)
                temp_set = [temp_docu_id_list, temp_docu_string_list, temp_feature_name, temp_count_matrix,
                            temp_page_rank_dic]

                with open(self.docu_info_path + ".txt", mode="wb") as fp:
                    pickle.dump(self.docu_info_dic, fp)

                with open(file_dir, mode="wb") as fp:
                    pickle.dump(temp_set, fp)

                temp_docu_id_list = []
                temp_docu_string_list = []
                temp_feature_name = None
                temp_count_matrix = None
                temp_page_rank_dic = None

                file_index += 1

        if len(temp_docu_id_list) != 0 :
            with open(self.docu_info_path + ".txt", mode="wb") as fp:
                pickle.dump(self.docu_info_dic, fp)

            file_dir = self.division_path + "_" + str(file_index) + ".txt"
            temp_feature_name, temp_count_matrix, temp_page_rank_dic = self.get_matrix_info(temp_docu_id_list, temp_docu_string_list)

            # temp_docu_id_list, temp_docu_string_list, temp_feature_name, temp_count_matrix, temp_page_rank_dic
            temp_set = [temp_docu_id_list, temp_docu_string_list, temp_feature_name, temp_count_matrix, temp_page_rank_dic]
            with open(file_dir, mode="wb") as fp:
                pickle.dump(temp_set, fp)


    def get_matrix_info(self, temp_docu_id_list, temp_string_list):
        vctr = CountVectorizer()
        tfvtr = TfidfVectorizer()

        temp_count_matrix = vctr.fit_transform(temp_string_list).toarray()  # 문제 생기면 아래로 바꾸자
        temp_feature_name = vctr.get_feature_names()
        temp_tfidf_matrix = tfvtr.fit_transform(temp_string_list).toarray()
        temp_page_rank_dic = self.get_page_rank(temp_docu_id_list, temp_tfidf_matrix)

        return temp_feature_name, temp_count_matrix, temp_page_rank_dic


    def get_page_rank(self, temp_docu_id_list, temp_tfidf_matrix):
        tfidf_mat = np.asarray(temp_tfidf_matrix)
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
        textrank_dictionary = {idx: r[0] for idx, r in zip(temp_docu_id_list, ranks)}
        return textrank_dictionary


    def stemming_user_query(self, search_query):
        remove_pos = "[(?P<조사>JK.*)(?P<접속조사>JC.*)(?P<전성어미>ET.*)(?P<종결어미>EF.*)(?P<연결어미>EC.*)(?P<접미사>XS.*)(?P<마침표물음표느낌표>SF.*)(?P<쉼표가운뎃점콜론빗금>SC.*)]"  # mecab
        mecab = Mecab()
        stemmed_words = mecab.pos(search_query)
        stemmed_words = [x[0] for x in stemmed_words if not bool(re.match(remove_pos, x[1]))]

        return ' '.join(stemmed_words)

    def search_news_document(self, search_query, result_n=5):
        user_query = self.stemming_user_query(search_query)

        pointer = len(self.docu_info_dic)
        if pointer == 0 :
            print("There is no document added. Please add the document list.")
            return None

        if pointer%self.batch_size == 0 and pointer/self.batch_size != 0 :
            file_index = int(m.floor(pointer / self.batch_size))
        else :
            file_index = int(m.floor(pointer / self.batch_size)) + 1

        search_document_id_list = []
        search_document_string_list = []


        end_file_index = file_index + 1

        for i in range(1, end_file_index):
            file_dir = self.division_path + "_" + str(file_index) + ".txt"
            # temp_docu_id_list, temp_docu_string_list, temp_feature_name, temp_count_matrix, temp_page_rank_dic
            try :
                with open(file_dir, mode="rb") as fp:
                    temp_docu_id_list, temp_docu_string_list, temp_feature_name, temp_count_matrix, temp_page_rank_dic = pickle.load(fp)
            except :
                continue

            division_top_n_list = self.get_top_n_from_division(user_query, temp_docu_id_list, temp_docu_string_list, temp_feature_name, temp_count_matrix, temp_page_rank_dic)  # 각 division에서 해당 쿼리에 가장 유사한 10개의 document_id의 리스트 반환
            division_top_n_string = [self.docu_string_list[self.docu_id_list.index(id)] for id in division_top_n_list]
            search_document_id_list = search_document_id_list + division_top_n_list
            search_document_string_list = search_document_string_list + division_top_n_string

        while len(search_document_id_list) > 2000 :
            temp_docu_id_list = search_document_id_list[0:2000]
            temp_docu_string_list = search_document_string_list[0:2000]
            search_document_id_list = search_document_id_list[2000:len(search_document_id_list)]
            search_document_string_list = search_document_string_list[2000:len(search_document_string_list)]

            try :
                temp_feature_name, temp_count_matrix, temp_page_rank_dic = self.get_matrix_info(temp_docu_id_list, temp_docu_string_list)
                reduced_docu_id_list = self.get_top_n_from_division(user_query, temp_docu_id_list, temp_docu_string_list, temp_feature_name, temp_count_matrix, temp_page_rank_dic)
                reduced_docu_string_list = [self.docu_string_list[self.docu_id_list.index(id)] for id in reduced_docu_id_list]
            except :
                reduced_docu_id_list = []
                reduced_docu_string_list = []
            search_document_id_list = search_document_id_list + reduced_docu_id_list
            search_document_string_list = search_document_string_list + reduced_docu_string_list

        if len(search_document_id_list) != 0 :
            search_feature_name, search_count_matrix, search_page_rank_dic = self.get_matrix_info(search_document_id_list, search_document_string_list)
            search_result = self.get_top_n_from_division(user_query, search_document_id_list, search_document_string_list, search_feature_name, search_count_matrix, search_page_rank_dic, n=result_n)
            return search_result
        else :
            print("There is no matched result.")
            return None


    def recommend_news_document(self, viewed_query, result_n=5):
        user_query = self.stemming_user_query(viewed_query)

        pointer = len(self.docu_info_dic)
        if pointer == 0 :
            print("There is no document added. Please add the document list.")
            return None

        if pointer%self.batch_size == 0 and pointer/self.batch_size != 0 :
            file_index = int(m.floor(pointer / self.batch_size))
        else :
            file_index = int(m.floor(pointer / self.batch_size)) + 1

        search_document_id_list = []
        search_document_string_list = []

        end_file_index = file_index - 3

        for i in range(file_index, end_file_index, -1):
            file_dir = self.division_path + "_" + str(file_index) + ".txt"
            # temp_docu_id_list, temp_docu_string_list, temp_feature_name, temp_count_matrix, temp_page_rank_dic
            try :
                with open(file_dir, mode="rb") as fp:
                    temp_docu_id_list, temp_docu_string_list, temp_feature_name, temp_count_matrix, temp_page_rank_dic = pickle.load(fp)
            except :
                continue

            division_top_n_list = self.get_top_n_from_division(user_query, temp_docu_id_list, temp_docu_string_list, temp_feature_name, temp_count_matrix, temp_page_rank_dic)  # 각 division에서 해당 쿼리에 가장 유사한 10개의 document_id의 리스트 반환
            division_top_n_string = [self.docu_string_list[self.docu_id_list.index(id)] for id in division_top_n_list]
            search_document_id_list = search_document_id_list + division_top_n_list
            search_document_string_list = search_document_string_list + division_top_n_string

        while len(search_document_id_list) > 2000 :
            temp_docu_id_list = search_document_id_list[0:2000]
            temp_docu_string_list = search_document_string_list[0:2000]
            search_document_id_list = search_document_id_list[2000:len(search_document_id_list)]
            search_document_string_list = search_document_string_list[2000:len(search_document_string_list)]

            try :
                temp_feature_name, temp_count_matrix, temp_page_rank_dic = self.get_matrix_info(temp_docu_id_list, temp_docu_string_list)
                reduced_docu_id_list = self.get_top_n_from_division(user_query, temp_docu_id_list, temp_docu_string_list, temp_feature_name, temp_count_matrix, temp_page_rank_dic)
                reduced_docu_string_list = [self.docu_string_list[self.docu_id_list.index(id)] for id in reduced_docu_id_list]
            except :
                reduced_docu_id_list = []
                reduced_docu_string_list = []
            search_document_id_list = search_document_id_list + reduced_docu_id_list
            search_document_string_list = search_document_string_list + reduced_docu_string_list

        if len(search_document_id_list) != 0 :
            search_feature_name, search_count_matrix, search_page_rank_dic = self.get_matrix_info(search_document_id_list, search_document_string_list)
            search_result = self.get_top_n_from_division(user_query, search_document_id_list, search_document_string_list, search_feature_name, search_count_matrix, search_page_rank_dic, n=result_n)
            return search_result
        else :
            print("There is no matched result.")
            return None


    def get_top_n_from_division(self, user_query, temp_docu_id_list, temp_docu_string_list, temp_feature_name, temp_count_matrix, temp_page_rank_dic, n=10):
        col_index = []
        for query in user_query.split():
            if query in temp_feature_name:
                col_index.append(temp_feature_name.index(query))

        if len(col_index) == 0:
            empty_list = []
            return empty_list

        target_columns = temp_count_matrix[:, col_index]
        target_document_id = np.array(temp_docu_id_list)[np.sum(target_columns, axis=1) != 0]

        target_dictionary = {k: v for k, v in temp_page_rank_dic.items() if k in target_document_id}
        sorted_target_list = sorted(target_dictionary, key=lambda k: target_dictionary[k], reverse=True)[0:n]

        return sorted_target_list
