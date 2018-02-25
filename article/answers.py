# -*- coding: utf-8 -*-


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from crawler.get_news import get_news, get_summary, get_news_by_id, get_category_by_doc_id, get_press_by_doc_id_category, get_latest_news
from article.models import Requirement, UserStatus, NewsRecord
from article.lists import press_list, date_list, category_list, gender_list, birth_year_list, region_list, \
    first_button_list, agree_disagree_news_save_list, end_of_service_list, maintain_remove_news_save_list
from crawler.models import *
from collections import Counter
from article.user_info_class import news_record, user_status, user_information_manager
from article.save_user_info import save_user_status
from django.utils import timezone
import article.content_based_cf as cb
import os

'''
/article/answers.py

'''
date = {}
category = {}
press = {}
user_request = {}
selected_news_title = {}
news_title_list = {}
prev_select = {}

user_info_gender = {}
user_info_birth_year = {}
user_info_region = {}
page_number = 0

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
user_info_manager = user_information_manager(path=os.path.join(BASE_DIR, 'info_matrix.txt'))


@csrf_exempt
def message(request):
    global date
    global category
    global press
    global user_request
    global selected_news_title
    global news_title_list
    global prev_select

    global user_info_gender
    global user_info_birth_year
    global user_info_region

    global user_info_manager

    global page_number

    '''
    :param 고객이 버튼을 눌렀을 경우 작동하는 함수로아래와 같은 정보가 전달된다.
    user_key: request.body.user_key, //user_key
    type: request.body.type,         //메시지 타입
    content: request.body.content    //메시지 내용
    :return JsonResponse 를 통해 message 와 keyboard(optional)가 반환된다.
    '''
    message = request.body.decode('utf-8')
    return_json_str = json.loads(message)
    content = return_json_str['content']
    user_key = return_json_str['user_key']

    # time out error 를 피하기 위한 트릭
    is_first_use = check_is_first_use(content, user_key)
    is_latest_news = check_is_latest_new(content)
    is_press = check_is_in_press_list(content)
    is_date = check_is_in_date_list(content)
    is_category = check_is_in_category_list(content)
    is_news_title = check_is_news_title(content, user_key)
    agree_flag1, agree_flag2 = check_is_agree_or_disagree(content, user_key)
    is_in_gender = check_is_in_gender_list(content)
    is_in_birth_year = check_is_in_birth_year_list(content)
    is_in_region_list = check_is_in_region_list(content)
    is_tutorial = check_is_in_tutorial(content)
    is_news_select = check_is_in_news_select(content)
    is_saved_news = check_is_saved_news(content)
    is_recent_news = check_is_recent_news(content)
    is_save_news_title = check_is_save_news_title(content)
    is_end_of_service = check_is_in_end_of_service_list(content)

    if is_latest_news:
        page_number += 1
        print("is latest news")
        from_number = 10 * (page_number - 1)
        to_number = 10 * page_number
        user_request[user_key], return_list = get_latest_news(from_number, to_number)
        return_list += ['view more']

        return JsonResponse({'message': {'text': '최신뉴스 목록 ' + str(page_number) + '페이지 입니다'},
                             'keyboard': {'type': 'buttons',
                                          'buttons': return_list}
                             })

    elif content == u'유사 이용자 검색':
        print('유사 이용자 검색')
        user_key_list = user_info_manager.get_n_similar_user(user_key, 1)  # 임의의 숫자 1
        print(user_key_list)
        news_id_list = user_info_manager.get_document_by_user_key(user_key_list[0])
        print(news_id_list)
        user_request[user_key] = get_news_by_id(news_id_list)
        return_list = list(user_request[user_key].keys())
        print(return_list)
        return JsonResponse({'message': {'text': '유사 이용자의 뉴스 검색 결과 입니다.'},
                             'keyboard': {'type': 'buttons',
                                          'buttons': return_list}
                             })

    elif content == u'유사 내용 검색':
        print('유사 내용 검색')
        from_date = (timezone.now() - timezone.timedelta(days=3)).strftime('%Y-%m-%d')
        to_date = timezone.now().strftime('%Y-%m-%d')
        searcher = cb.news_searcher("content_base.txt")
        news_id_list = list(
            PoliticsDocument.objects.filter(crawled_date__range=[from_date, to_date]).values_list('document_id',
                                                                                                  flat=True))
        news_id_list += list(
            EconomicsDocument.objects.filter(crawled_date__range=[from_date, to_date]).values_list('document_id',
                                                                                                   flat=True))
        news_id_list += list(
            SocietyDocument.objects.filter(crawled_date__range=[from_date, to_date]).values_list('document_id',
                                                                                                 flat=True))
        news_id_list += list(
            CultureLivingDocument.objects.filter(crawled_date__range=[from_date, to_date]).values_list('document_id',
                                                                                                       flat=True))
        news_id_list += list(
            WorldDocument.objects.filter(crawled_date__range=[from_date, to_date]).values_list('document_id',
                                                                                               flat=True))
        news_id_list += list(
            ITScienceDocument.objects.filter(crawled_date__range=[from_date, to_date]).values_list('document_id',
                                                                                                   flat=True))
        print(news_id_list)
        searcher.add_new_document(news_id_list)
        search_query = "북한 열병식"  # 임의의 쿼리문
        print('search_query: ' + search_query)
        news_id_list = searcher.search_news_document(search_query, 10)
        print(news_id_list)
        user_request[user_key] = get_news_by_id(news_id_list)
        return_list = list(user_request[user_key].keys())
        print(return_list)
        return JsonResponse({'message': {'text': '유사 뉴스 검색 결과 입니다.'},
                             'keyboard': {'type': 'buttons',
                                          'buttons': return_list}
                             })

    elif is_end_of_service:
        if content == 'stop':
            reset_globals(user_key)
            return JsonResponse({'message': {'text': 'you select stop'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': first_button_list}
                                 })
        elif content == 'break':
            reset_globals(user_key)
            return JsonResponse({'message': {'text': 'you select break'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': date_list}
                                 })
        else:
            if prev_select.get(user_key) is not None:
                return_list = add_index_of_list(list(user_request[user_key].keys()))
            else:
                return_list = list(user_request[user_key].keys())

            print(return_list)
            return JsonResponse({'message': {'text': 'you select continue'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': return_list}
                                 })
    elif is_tutorial:
        print('tutorial page')

        return JsonResponse({'message': {'text': '사용방법 안내 문구'},
                             'keyboard': {'type': 'buttons',
                                          'buttons': first_button_list}
                             })

    elif is_news_select:
        print('news_select_page')

        return JsonResponse({'message': {'text': '우선 날짜부터 골라주세요!'},
                             'keyboard': {'type': 'buttons',
                                          'buttons': date_list}
                             })

    elif is_saved_news:
        print('is_saved_news')
        prev_select[user_key] = '저장한 뉴스'

        user_status_object = UserStatus.objects.get(user_key=user_key)
        news_requirement = NewsRecord.objects.filter(
            user_status=user_status_object,
            is_scraped=True
        ).order_by("-request_time")[:20]
        print('저장한 뉴스 보여주기')
        return1 = dict(news_requirement.values_list('request_title', 'request_news_id'))
        user_request[user_key] = return1
        print("in_saved_news: " + str(user_request[user_key]))
        result_list = add_index_of_list(list(return1.keys()))
        print(result_list)

        if len(result_list) > 0:
            return JsonResponse({'message': {'text': '저장했던 뉴스입니다.'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': result_list}
                                 })
        else:
            print('최근에 본 뉴스가 없을 경우')
            return JsonResponse({'message': {'text': '저장하신 뉴스가 없습니다'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': end_of_service_list}
                                 })
    elif is_recent_news:
        print('is_recent_news')
        prev_select[user_key] = '최근 본 뉴스'

        user_status_object = UserStatus.objects.get(user_key=user_key)
        news_requirement = NewsRecord.objects.filter(
            user_status=user_status_object,
        ).order_by("-request_time")[:20]
        return1 = dict(news_requirement.values_list('request_title', 'request_news_id'))
        user_request[user_key] = return1
        result_list = add_index_of_list(list(return1.keys()))
        print(result_list)

        if len(result_list) > 0:
            return JsonResponse({'message': {'text': '최근에 보신 뉴스입니다.'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': result_list}
                                 })
        else:
            print('최근에 본 뉴스가 없을 경우')
            return JsonResponse({'message': {'text': '최근에 보신 뉴스가 없습니다'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': end_of_service_list}
                                 })

    elif is_date:
        reset_globals(user_key)
        date[user_key] = content
        print("selected day is " + date[user_key] + "일")
        return1 = handle_request(user_key)
        if isinstance(return1, dict):
            if return1.get("none") is not None:
                reset_globals(user_key)
                return JsonResponse({'message': {'text': '선택이 모두 완료되었지만, 해당하는 기사가 없습니다.'},
                                     'keyboard': {'type': 'buttons',
                                                  'buttons': first_button_list}
                                     })
            result_list = []
            for i in return1.keys():
                result_list.append(return1[i])

            print(result_list)
            user_request[user_key] = result_list

            return JsonResponse({'message': {'text': '선택이 모두 완료되었습니다. 관심있는 기사가 있으신가요?'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': result_list}
                                 })
        else:
            print(category_list)
            return JsonResponse({'message': {'text': str(return1) + "분야를 선택해 주세요"},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': category_list}
                                 })

    elif is_category:
        category[user_key] = content
        print("selected category is" + category[user_key])
        return1 = handle_request(user_key)

        if isinstance(return1, dict):
            print("is_full and is_category")
            if return1.get("none") is not None:
                reset_globals(user_key)
                return JsonResponse({'message': {'text': '선택이 모두 완료되었지만, 해당하는 기사가 없습니다.'},
                                     'keyboard': {'type': 'buttons',
                                                  'buttons': date_list}
                                     })

            result_list = []
            for i in return1.keys():
                result_list.append(i)

            print(result_list)
            user_request[user_key] = return1
            print(user_request[user_key])
            return JsonResponse({'message': {'text': '선택이 모두 완료되었습니다. 관심있는 기사가 있으신가요?'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': result_list}
                                 })
        else:
            return_press_list = make_press_list(content, user_key)
            print(return_press_list)

            if len(return_press_list) is 0:
                reset_globals(user_key)
                return JsonResponse({'message': {'text': '날짜와 카테고리에 맞는 신문사가 없습니다. 다시 골라 주세요'},
                                     'keyboard': {'type': 'buttons',
                                                  'buttons': date_list}
                                     })

            return JsonResponse({'message': {'text': str(return1) + "다른것을 선택해 주세요"},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': return_press_list}
                                 })

    elif is_press:
        if content == '--------------------':
            print('구분자를 선택한 상황임')

            return_press_list = make_press_list(category[user_key], user_key)
            print(return_press_list)

            return JsonResponse({'message': {'text': '신문사를 다시 골라주세요'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': return_press_list}
                                 })

        separator = ' '
        rest = content.rsplit(separator, 1)[0]
        press[user_key] = rest
        print("selected press is " + press[user_key])
        return1 = handle_request(user_key)

        if isinstance(return1, dict):
            if return1.get("none") is not None:
                reset_globals(user_key)
                return JsonResponse({'message': {'text': '선택이 모두 완료되었지만, 해당하는 기사가 없습니다.'},
                                     'keyboard': {'type': 'buttons',
                                                  'buttons': first_button_list}
                                     })

            result_list = list(return1.keys())
            news_title_list[user_key] = result_list
            user_request[user_key] = return1

            return JsonResponse({'message': {'text': '선택이 모두 완료되었습니다. 관심있는 기사가 있으신가요?'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': result_list}
                                 })
        else:
                return JsonResponse({'message': {'text': str(return1) + "날짜를 선택해 주세요"},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': date_list}
                                 })

    elif is_news_title:

        doc_id = str(user_request.get(user_key).get(content))
        if doc_id == 'None':
            rest = content.split(' ', 1)[1]
            print("rest: " + rest)
            doc_id = str(user_request.get(user_key).get(rest))

        print("in_is_news_title: " + doc_id)
        category[user_key] = get_category_by_doc_id(doc_id)
        print(category[user_key])
        press[user_key] = get_press_by_doc_id_category(doc_id, category[user_key])
        print(press[user_key])

        selected_news_title[user_key], text, url, published_date = get_summary(doc_id, category[user_key])
        print(category.get(user_key))
        print(press.get(user_key))

        if len(NewsRecord.objects.filter(request_news_id=doc_id)) == 0:
            news_info = {"document_id": doc_id, "press": press.get(user_key),
                         "category": category.get(user_key), "title": selected_news_title[user_key],
                         "request_time": timezone.now().strftime("%Y-%m-%d %H:%M")}

            news_record_instance = news_record(**news_info)
            user_info_manager.update_user_record(user_key, news_record_instance)
        else:
            news_record_update = NewsRecord.objects.get(request_news_id=doc_id)
            news_record_update.request_time = timezone.now().strftime("%Y-%m-%d %H:%M")
            news_record_update.save()

        print(selected_news_title[user_key])
        print(text)
        print(url)
        print(published_date)

        if prev_select.get(user_key) == '최근 본 뉴스' or prev_select.get(user_key) == '저장한 뉴스':
            return_button_list = maintain_remove_news_save_list
            del prev_select[user_key]
        else:
            return_button_list = agree_disagree_news_save_list

        print(return_button_list)
        return JsonResponse({'message': {"text": selected_news_title[user_key] + "\n————————————---\n"
                                                 + category.get(user_key) + ', ' + press.get(user_key) + ', ' + str(published_date) +
                                                 '\n—————---———————\n'
                                                 + text + "\n————————---————\n"
                                                 + url
                                         },
                             'keyboard': {'type': 'buttons',
                                          'buttons': return_button_list}
                             })

    elif is_save_news_title:
        if content == u'뉴스를 저장하겠습니다':
            print(content)

            doc_id = str(user_request.get(user_key).get(selected_news_title[user_key]))

            news_scrap = NewsRecord.objects.get(request_news_id=doc_id)
            news_scrap.is_scraped = True
            news_scrap.save()

            return JsonResponse({'message': {"text": "뉴스가 저장되었습니다. 저장하신 뉴스 정보는 일주일간 보관합니다"},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': end_of_service_list}
                                 })
        elif content == u'뉴스를 저장하지 않겠습니다.':
            print(content)
            return JsonResponse({'message': {'text': '뉴스가 저장되지 않았습니다.'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': end_of_service_list}
                                 })
        elif content == u'유지하기':
            print(content)
            return JsonResponse({'message': {'text': '뉴스가 유지 되었습니다.'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': end_of_service_list}
                                 })
        elif content == u'삭제하기':
            print(content)
            doc_id = str(user_request.get(user_key).get(selected_news_title[user_key]))

            news_scrap = NewsRecord.objects.get(request_news_id=doc_id)
            news_scrap.is_scraped = False
            news_scrap.save()

            return JsonResponse({'message': {'text': '뉴스가 삭제 되었습니다.'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': end_of_service_list}
                                 })

    elif agree_flag1:
        print("최초 개인 정보 수집에 대한 답변입니다.")

        if len(UserStatus.objects.filter(user_key=user_key)) != 0:
            print('이미 입력하신 정보가 있습니다')
            print(first_button_list)
            return JsonResponse({'message': {'text': '이미 입력하신 정보가 있습니다.\n[[기본 안내문구]]'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': first_button_list}
                                 })

        elif agree_flag2:
            print("동의합니다")
            print(gender_list)
            return JsonResponse(
                {'message': {'text': '동의해 주셔서 감사합니다. 원활한 서비스 제공을 위해 성별/나이/직업/지역에 대한 기본적인 정보수집을 진행하겠습니다.\n성별을 선택해주세요.'},
                 'keyboard': {'type': 'buttons',
                              'buttons': gender_list}
                 })

        else:
            print("동의하지 않습니다")
            user_status_save = UserStatus(
                user_key=user_key
            )
            user_status_save.save()

            return JsonResponse({'message': {'text': '정보수집에 동의 하지 않으셨습니다.\n[[기본 안내문구]]'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': date_list}
                                 })

    elif is_in_gender:
        print('성별에 대한 답변을 한 상태' + str(content))
        user_info_gender[user_key] = content
        print(user_info_gender)
        print(birth_year_list)
        return JsonResponse({'message': {'text': '감사합니다. 출생년도를 입력해 주시겠어요?'},
                             'keyboard': {'type': 'buttons',
                                          'buttons': birth_year_list}
                             })

    elif is_in_birth_year:
        print('생년에 대한 답변을 한 상태' + str(content))
        user_info_birth_year[user_key] = content
        print(user_info_birth_year)
        print(region_list)
        return JsonResponse({'message': {'text': '마지막으로 지역을 입력해 주시겠어요?'},
                             'keyboard': {'type': 'buttons',
                                          'buttons': region_list}
                             })

    elif is_in_region_list:
        print('지역 답변까지 완료를 한 상태' + str(content))
        user_info_region[user_key] = content
        print(user_info_region)

        user_info = {'user_key': user_key, 'gender': user_info_gender[user_key],
                     'birth_year': user_info_birth_year[user_key], 'location': user_info_region[user_key]}
        user_status_instance = user_status(**user_info)
        save_user_status(user_status_instance)

        show_result = "성별: " + str(user_info_gender[user_key]) + \
                      "\n생년: " + str(user_info_birth_year[user_key]) + \
                      "\n지역: " + str(user_info_region[user_key])
        del user_info_gender[user_key]
        del user_info_region[user_key]
        del user_info_birth_year[user_key]
        print(show_result)

        return JsonResponse({'message': {'text': show_result + '\n정보 수집이 모두 완료되었습니다. 감사합니다.\n[[기본안내문구]]'},
                             'keyboard': {'type': 'buttons',
                                          'buttons': first_button_list}
                             })
    elif is_first_use:
        print("UserStatus 가 없는 경우에 적용함")
        button_list = ['동의합니다', '동의하지 않습니다']
        return JsonResponse({'message': {'text': '안녕하세요! 처음 이용하사네요! 저희 서비스는 뉴스 요약문을 제공하는 서비스 입니다.\n'
                                                 '원활한 서비스 제공을 위해 사용자의 기본적인 개인정보를 수집하고 있습니다! 개인정보 제공에 동의하시나요?'},
                             'keyboard': {'type': 'buttons',
                                          'buttons': button_list}
                             })
    else:
        print("정의되지 않은 구문")
        reset_globals(user_key)

        similar_list = user_info_manager.get_n_similar_user(user_key, 3)
        print(similar_list)

        return JsonResponse({'message': {'text': '죄송합니다 정의되지 않은 응답입니다.'},
                             'keyboard': {'type': 'buttons',
                                          'buttons': first_button_list}
                             })


def check_is_recent_news(content):
    if content == u'최근 본 뉴스':
        return True
    else:
        return False


def check_is_latest_new(content):
    if content == u'최신 뉴스 보기' or content == u'view more':
        return True
    else:
        return False


def check_is_first_use(content, user_key):
    if len(UserStatus.objects.filter(user_key=user_key)) == 0:
        return True
    else:
        return False


def check_is_in_end_of_service_list(content):
    if content in end_of_service_list:
        return True
    else:
        return False


def check_is_save_news_title(content):
    if content in agree_disagree_news_save_list:
        return True
    elif content in maintain_remove_news_save_list:
        return True
    else:
        return False


def check_is_saved_news(content):
    if content == u'저장한 뉴스':
        return True
    else:
        return False


def check_is_in_tutorial(content):
    if content == u'사용 방법 보기':
        return True
    else:
        return False


def check_is_in_news_select(content):
    if content == u'뉴스 검색':
        return True
    else:
        return False


# 지역을 선택한 상황인가
def check_is_in_region_list(content):
    if content in region_list:
        return True
    else:
        return False


# 나이대 선택을 한 상황인가
def check_is_in_birth_year_list(content):
    if content in birth_year_list:
        return True
    else:
        return False


# 성별 선택을 한 상황인가
def check_is_in_gender_list(content):
    if content in gender_list:
        return True
    else:
        return False


# 정보수집 여부에 대한 답변인가
def check_is_agree_or_disagree(content, user_key):
    if content == u'동의합니다':
        return True, True
    elif content == u'동의하지 않습니다':
        return True, False
    else:
        return False, False


# 날짜 목록중 하나인지 체크
def check_is_in_date_list(content):
    if content in date_list:
        return True
    else:
        return False


# 카테고리 중 하나인지 체크
def check_is_in_category_list(content):
    if content in category_list:
        return True
    else:
        return False


# 신문사 이름중 하나인지 확인
def check_is_in_press_list(content):
    separator = ' '
    rest = content.rsplit(separator, 1)[0]
    print(rest)
    if rest in press_list:
        return True
    else:
        return False


# 뉴스를 요청하는 것인지확인
def check_is_news_title(content, user_key):
    global user_request
    separator = ' '
    rest = ''
    try:
        rest = content.split(separator, 1)[1]
        print(rest)
    except Exception as e:
        print(e)

    if user_request.get(user_key) is None:
        return False
    else:
        print(user_request.get(user_key))
        if content in user_request.get(user_key).keys():
            return True
        elif rest in user_request.get(user_key).keys():
            return True
        else:
            return False


# 전부다 선택했는지 확인
def is_full(user_key):
    global press
    global date
    global category

    if date.get(user_key) is None:
        return False
    elif category.get(user_key) is None:
        return False
    elif press.get(user_key) is None:
        return False
    else:
        return True


# 고객 요청 처리 간소화
@csrf_exempt
def handle_request(user_key):
    global press
    global category
    global date

    if is_full(user_key):
        print("is_full")
        rq_date = date[user_key][0:4] + "년 " + date[user_key][5:7] + "월 " + date[user_key][8:10] + "일"
        save_request = Requirement(user_key=user_key, press=press[user_key], date=rq_date, category=category[user_key])
        save_request.save()
        response = get_news(press[user_key], date[user_key], category[user_key])
        print(response)

        return response

    else:
        print_result = ""

        if press.get(user_key) is not None:
            print_result = "[" + press.get(user_key) + "] " + print_result
            print(print_result)

        if category.get(user_key) is not None:
            print_result = "[" + category.get(user_key) + "]" + print_result
            print(print_result)

        if date.get(user_key) is not None:
            print_result = "[" + date.get(user_key) + "]" + print_result
            print(print_result)

        return print_result


def reset_globals(user_key):
    global date
    global category
    global press
    global user_request
    global selected_news_title
    global news_title_list
    global page_number

    try:
        del press[user_key]
    except Exception as e:
        print("신문사 아직 안골라서 못지움")

    try:
        del date[user_key]
    except Exception as e:
        print("날짜 아직 안골라서 못지움")

    try:
        del category[user_key]
    except Exception as e:
        print("분야 아직 안골라서 못지움")

    try:
        del user_request[user_key]
    except Exception as e:
        print("뉴스가 없어서 저장을 못했는데 어떻게 지우냐 멍청아!")

    try:
        del selected_news_title[user_key]
    except Exception as e:
        print('고른 기사가 없어서 못지움')

    try:
        del news_title_list[user_key]
    except Exception as e:
        print('뉴스 리스트가 없어서 못 지움')

    page_number = 0


# global result 라는 변수 하나만을 선언해서 result = {'encrypted_user_key':{'press':'조선일보','year':'2018','category':'정치'}} 등으로 처리해보자

def make_press_list(content, user_key):
    global date
    return_press_list = []
    additional_press_list = []

    if content == "정치":
        return_press_list = list(PoliticsDocument.objects.filter(
            published_date__year=int(date.get(user_key)[0:4]),
            published_date__month=int(date.get(user_key)[5:7]),
            published_date__day=int(date.get(user_key)[8:10]),
        ).values_list('press', flat=True))

    elif content == "경제":
        return_press_list = list(EconomicsDocument.objects.filter(
            published_date__year=int(date.get(user_key)[0:4]),
            published_date__month=int(date.get(user_key)[5:7]),
            published_date__day=int(date.get(user_key)[8:10]),
        ).values_list('press', flat=True))

    elif content == "사회":
        return_press_list = list(SocietyDocument.objects.filter(
            published_date__year=int(date.get(user_key)[0:4]),
            published_date__month=int(date.get(user_key)[5:7]),
            published_date__day=int(date.get(user_key)[8:10]),
        ).values_list('press', flat=True))

    elif content == "생활/문화":
        return_press_list = list(CultureLivingDocument.objects.filter(
            published_date__year=int(date.get(user_key)[0:4]),
            published_date__month=int(date.get(user_key)[5:7]),
            published_date__day=int(date.get(user_key)[8:10]),
        ).values_list('press', flat=True))

    elif content == "세계":
        return_press_list = list(WorldDocument.objects.filter(
            published_date__year=int(date.get(user_key)[0:4]),
            published_date__month=int(date.get(user_key)[5:7]),
            published_date__day=int(date.get(user_key)[8:10]),
        ).values_list('press', flat=True))

    elif content == "IT/과학":
        return_press_list = list(ITScienceDocument.objects.filter(
            published_date__year=int(date.get(user_key)[0:4]),
            published_date__month=int(date.get(user_key)[5:7]),
            published_date__day=int(date.get(user_key)[8:10]),
        ).values_list('press', flat=True))

    # print(return_press_list)

    try:
        additional_press_list = list(NewsRecord.objects.filter(
            user_status=UserStatus.objects.get(user_key=user_key),
            request_time__gte=timezone.now() - timezone.timedelta(days=7)
        ).order_by('request_time').values_list('request_press', flat=True).distinct())
    except Exception as e:
        print(str(e))

    counter_press_list = Counter(return_press_list)

    result = []
    for i in counter_press_list:
        result.append(str(i) + ' (' + str(counter_press_list[i]) + ')')

    result.sort()
    result = ["--------------------"] + result

    additional_press_list = make_unique_list(additional_press_list)

    for i in reversed(range(len(additional_press_list))):
        if additional_press_list[i] in counter_press_list:
            print('앞에 추가될 신문사' + additional_press_list[i])
            result = [str(additional_press_list[i]) + " (" + str(
                counter_press_list.get(additional_press_list[i])) + ")"] + result

    return result


# list 를 넣어서 중복되는 것을 제거하는 함수
def make_unique_list(sequence):
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]


def add_index_of_list(input_list):
    return_list = []
    for i in range(len(input_list)):
        return_list += [str(i + 1) + '. ' + str(input_list[i])]
    return return_list
