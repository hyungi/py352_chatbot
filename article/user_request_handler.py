from article.lists import date_list, press_list, category_list
from article.models import NewsRequirement
from crawler.get_news import get_news, get_summary
from crawler.models import PoliticsDocument, SocietyDocument, EconomicsDocument, CultureLivingDocument, ITScienceDocument, WorldDocument
from django.utils import timezone


class UserRequestHandler:
    """
    class:
    """
    def __init__(self):
        self.date = {}
        self.press = {}
        self.category = {}
        self.summary = {}
        self.user_request = {}
        self.politics_document = {}
        self.society_document = {}
        self.economics_document = {}
        self.culture_living_document = {}
        self.it_science_document = {}
        self.world_document = {}

    # 날짜 목록중 하나인지 체크
    def check_is_in_date_list(self, user_key, content):
        if content in date_list:
            self.date[user_key] = content
            return True
        else:
            return False

    # 카테고리 중 하나인지 체크
    def check_is_in_category_list(self, user_key, content):
        if content in category_list:
            self.category[user_key] = content
            return True
        else:
            return False

    # 신문사 이름중 하나인지 확인
    def check_is_in_press_list(self, user_key, content):
        if content in press_list:
            self.press[user_key] = content
            return True
        else:
            return False

    # 뉴스를 요청하는 것인지확인
    def check_is_news_title(self, user_key, content):
        if self.user_request.get(user_key) is None:
            return False
        else:
            if 'title' in self.user_request.get(user_key).values('title'):
                dict_list = list(self.user_request.get(user_key))
                request_doc_id = ""

                for i in dict_list:
                    if i.get('title') == content:
                        request_doc_id = i.get('document_id')

                title, text, url = get_summary(request_doc_id, self.category.get(user_key))

                self.summary[user_key] = [title, text, url]

                news_requirement = NewsRequirement(
                    user_key=user_key,
                    request_news_title=title,
                    request_news_id=request_doc_id
                )
                news_requirement.save()
                # self.category.get(user_key)
                self.reset(user_key)
                return True
            else:
                return False

    def reset(self, user_key):
        """
        사용자가 이용의 마지막 단계에 이르면 마지막으로 요청한 정보를 보내고
        클래스 내부의 변수들을 모두 초기화 하는 함수
        :param user_key:
        :return: None
        """
        del self.date[user_key]
        del self.category[user_key]
        del self.press[user_key]

        del self.politics_document[user_key]
        del self.society_document[user_key]
        del self.economics_document[user_key]
        del self.culture_living_document[user_key]
        del self.it_science_document[user_key]
        del self.world_document[user_key]

        try:
            del self.user_request[user_key]

        except Exception as e:
            print("JALHAZA")

    def is_full(self, user_key):
        """
        사용자가 기본적인 요구사항을 모두 입력하여 10개의 기사를 보내주는 서비스를 실행해야 하는지 판단하는 함수
        :param user_key:
        :return:
        """
        if self.date.get(user_key) is None:
            return False
        elif self.category.get(user_key) is None:
            return False
        elif self.press.get(user_key) is None:
            return False
        else:
            self.user_request[user_key] = sorted(self.user_request.get(user_key), key=lambda doc: doc.published_date, reverse=True)[0:10]
            # user_request = {'user_key':{'title1':'doc_id1','title2':'doc_id2'}}
            return True

    # 고객이 선택을 할때마다 쿼리를 돌려서 고객에게 제공하는 선택지를 유의미하게 줄여준다.
    def do_query(self, user_key, input_data):
        print("do_query " + input_data)
        """
        :param user_key:
        :param input_data:
        :return: None
        """
        return_list = []
        if input_data in date_list:
            year = int(input_data[0:4])
            month = int(input_data[6:7])
            day = int(input_data[9:10])

            self.politics_document[user_key] = PoliticsDocument.objects.filter(published_date__year=year)
            self.society_document[user_key] = SocietyDocument.objects.filter(published_date__year=year)
            self.economics_document[user_key] = EconomicsDocument.objects.filter(published_date__year=year)
            self.culture_living_document[user_key] = CultureLivingDocument.objects.filter(published_date__year=year)
            self.it_science_document[user_key] = ITScienceDocument.objects.filter(published_date__year=year)
            self.world_document[user_key] = WorldDocument.objects.filter(published_date__year=year)

            self.politics_document[user_key] = self.politics_document[user_key].filter(published_date__month=month)
            self.society_document[user_key] = self.society_document[user_key].filter(published_date__month=month)
            self.economics_document[user_key] = self.economics_document[user_key].filter(published_date__month=month)
            self.culture_living_document[user_key] = self.culture_living_document[user_key].filter(published_date__month=month)
            self.it_science_document[user_key] = self.it_science_document[user_key].filter(published_date__month=month)
            self.world_document[user_key] = self.world_document[user_key].filter(published_date__month=month)

            self.politics_document[user_key] = self.politics_document[user_key].filter(published_date__day=day)
            self.society_document[user_key] = self.society_document[user_key].filter(published_date__day=day)
            self.economics_document[user_key] = self.economics_document[user_key].filter(published_date__day=day)
            self.culture_living_document[user_key] = self.culture_living_document[user_key].filter(published_date__day=day)
            self.it_science_document[user_key] = self.it_science_document[user_key].filter(published_date__day=day)
            self.world_document[user_key] = self.world_document[user_key].filter(published_date__day=day)

        elif input_data in category_list:
            if input_data == '정치':
                self.user_request[user_key] = self.politics_document.get(user_key)
            elif input_data == '경제':
                self.user_request[user_key] = self.economics_document.get(user_key)
            elif input_data == '사회':
                self.user_request[user_key] = self.society_document.get(user_key)
            elif input_data == '생활/문화':
                self.user_request[user_key] = self.culture_living_document.get(user_key)
            elif input_data == '세계':
                self.user_request[user_key] = self.world_document.get(user_key)
            elif input_data == 'IT/과학':
                self.user_request[user_key] = self.it_science_document.get(user_key)

        elif input_data in press_list:
            self.user_request[user_key] = [i for i in self.user_request[user_key] if i.press == input_data]

            # "Cannot filter a query once a slice has been taken."
            # print("before filter "+str(self.user_request.get(user_key).count()))
            # print("after filter "+str(self.user_request.get(user_key).count()))
            # QuerySet 객체는 자체적으로 filter 함수를 쓰면 걸러진 결과가 QuerySet에 저장되지만,
            # QuerySet 을 다른곳에 저장한 뒤 접근하면 filter 를 해도 해당 결과가 저장 되는 것은 아니다.

