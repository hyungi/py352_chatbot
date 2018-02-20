import numpy as np
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import pairwise_distances
from crawler.models import DocumentId, DocumentSummary
from konlpy.tag import Mecab

class news_searcher:
    def __init__(self, path):
        '''
        content-based CF를 이용해 적합한 뉴스 기사를 찾아준다. 추천으로 활용 가능.
        :param path: document_list(각 document의 tf_vector를 원소로 갖는 list)을 저장할 path (string) 
        '''
        self.path = path
        self.dtm_index = []
        self.dtm_list = []
        self.dtm = None
        self.jaccard_matrix = None
        self.vctr = CountVectorizer()
        try: #파일이 존재하는 경우
            with open(self.path, mode="rb") as fp:
                self.dtm_index, self.dtm_list = pickle.load(fp)

            if len(self.dtm_index) == 0: #파일이 존재하지만 저장된 정보가 없을 경우
                print("Empty Document_Term_Matrix has been loaded.")
            else: #정보가 이미 저장된 파일이 존재하는 경우
                self.create_jaccard_matrix()
                print("Document_Term_Matrix has been loaded successfully.")

        except: #파일이 없는 경우 메세지를 띄우고 새로 빈 파일을 생성한다.
            print("There are no existing Document_Term_Matrix.")
            with open(self.path, mode="wb") as fp:
                pickle.dump([self.dtm_index, self.dtm_list], fp)
            print("New Document_Term_Matrix has been created.")

    def get_document_tfvector(self, document_id):
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
        self.create_jaccard_matrix()


    def save_updated_document_list(self):
        '''
        변경된 사항을 pickle을 이용해 저장한다.
        :return: None
        '''
        with open(self.path, mode="wb") as fp:
            pickle.dump([self.dtm_index, self.dtm_list], fp)


    def create_dtm(self):
        '''
        sklearn의 CountVectorizer을 이용해 주어진 리스트를 sparse_matrix 형태로 만든다.
        :return: None
        '''
        self.dtm = self.vctr.fit_transform(self.dtm_list).toarray()


    def create_jaccard_matrix(self):
        '''
        모든 document와 document의 유사도 정보를 갖는 jaccard_similar_matrix로 만든다. 
        :return: None
        '''
        self.create_dtm()
        self.jaccard_matrix = (1 - pairwise_distances(self.dtm, metric="hamming"))


    def get_similar_document(self, document_id, n):
        '''
        target document_id와 n을 입력 받아, n개의 유사한 document의 id를 반환한다.
        :param document_id: 유사한 대상을 찾고자 하는 타겟 document_id (string) 
        :param n: 찾고자 하는 유사한 document의 개수 (integer)
        :return: document_id를 원소로 갖는 리스트 (list)
        '''
        try:
            target_number = self.dtm_index.index(document_id)
        except:
            print("The document_id does not exist in Document_Term_Matrix.")

        top_n_index = np.argsort(self.jaccard_matrix[target_number])[-2:-(2 + n):-1]
        top_n_document = np.array(self.dtm_index)[np.array(top_n_index)]
        return list(top_n_document)


    def stemming_user_query(self, search_query):
        remove_pos = "[(?P<조사>JK.*)(?P<접속조사>JC.*)(?P<전성어미>ET.*)(?P<종결어미>EF.*)(?P<연결어미>EC.*)(?P<접미사>XS.*)(?P<마침표물음표느낌표>SF.*)(?P<쉼표가운뎃점콜론빗금>SC.*)]"  # mecab
        mecab = Mecab()
        stemmed_words = mecab.pos(search_query)
        stemmed_words = [x[0] for x in stemmed_words if not bool(re.match(remove_pos, x[1]))]

        return ' '.join(stemmed_words)

    def search_news_document(self, search_query, n):
        '''
        검색어와 jaccard_similarity가 가장 가까운 document의 id를 원소로 갖는 리스트를 반환한다.
        :param search_query: 찾고자 하는 검색어 (string)
        :param n: 유사한 document의 수 (integer) #보통 n=5 정도로 하자.
        :return: 검색어와 가장 유사한 document_id를 원소로 갖는 리스트 (list)
        '''

        #search_query를 기존 dtm에 맞는 vector 형태로 변환
        user_query = self.stemming_user_query(search_query)
        target_vector = self.vctr.transform([user_query]).toarray()

        #기존 dtm_index와 dtm_list에 영향을 주지 않기 위해 copy하고 copy된 객체 위에서 jaccard 거리 산출
        search_dtm_index = (self.dtm_index.copy())
        search_dtm_index.append("target_index")
        search_dtm = np.append((self.dtm.copy()), target_vector, axis=0)
        search_jaccard_matrix = (1 - pairwise_distances(search_dtm, metric="hamming"))

        #임시로 산출된 jaccard_matrix에서 검색어(user_query)와 가장 유사한 document의 id를 반환
        search_target = search_dtm_index.index("target_index")
        top_n_index = np.argsort(search_jaccard_matrix[search_target])[-2:-(2 + n):-1]
        top_n_document = np.array(self.dtm_index)[np.array(top_n_index)]

        return list(top_n_document)
