# -*- coding: utf-8 -*-


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from crawler.get_news import get_news, get_summary, get_news_by_id, get_category_by_doc_id, \
    get_press_by_doc_id_category, get_latest_news
from article.models import Requirement, UserStatus, NewsRecord
from article.lists import press_list, date_list, category_list, gender_list, birth_year_list, region_list, \
    first_button_list, agree_disagree_news_save_list, end_of_service_list, maintain_remove_news_save_list, \
    news_select_button_list, feedback_list, setting_list
from crawler.models import *
from collections import Counter
from article.user_info_class import news_record, user_status, user_information_manager
from article.save_user_info import save_user_status
from django.utils import timezone
import article.content_based_cf as cb
import os
import collections
from article.search_engine_manager import search_engine_manager

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

dtm_path = os.path.join(BASE_DIR, 'dtm.txt')
matrix_path = os.path.join(BASE_DIR, 'vctr')
path = {'dtm_path': dtm_path, 'matrix_path': matrix_path}
engine = search_engine_manager(**path)


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
    global engine

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

    is_news_keyword_search_select = check_is_in_news_keyword_search(content)
    is_news_date_search_select = check_is_in_news_date_search(content)

    is_feedback_list = check_is_in_feedback_list(content)
    is_feedback = check_is_feedback(content)

    is_setting_list = check_is_in_setting_list(content)
    is_setting = check_is_setting(content)

    if is_first_use:
        print("UserStatus 가 없는 경우에 적용함")
        button_list = ['동의합니다', '동의하지 않습니다']
        return JsonResponse({'message': {'text': '안녕하세요. 최신 뉴스를 요약해주는 “호외요”입니다. \n' +
                                                 '최신 뉴스는 물론, 날짜/관심 분야/신문사별로 원하는 뉴스를 검색하고 스크랩할 수 있는 서비스입니다. \n' +
                                                 '원활한 서비스 제공을 위해 사용자의 기본 정보를 수집하고 있습니다. 수집한 정보는 맞춤형 뉴스 추천, 이용자 통계 서비스 제공에 사용됩니다. 개인정보 제공에 동의하시나요? \n'
                                         },
                             'keyboard': {'type': 'buttons',
                                          'buttons': button_list}
                             })
    elif is_setting:
        print(content)
        print(setting_list)
        return JsonResponse({'message': {'text': '설정 메뉴 입니다.'},
                             'keyboard': {'type': 'buttons',
                                          'buttons': setting_list}
                             })

    elif is_setting_list:
        print(content)
        print(first_button_list)
        user_status_instance = UserStatus.objects.get(user_key=user_key)

        if content == setting_list[0]:
            user_status_instance.recommend_service = False
            user_status_instance.save()
        elif content == setting_list[1]:
            news_record_instance = NewsRecord.objects.get(user_status=user_status_instance)
            news_record_instance.delete()
        else:
            news_record_instance = NewsRecord.objects.get(user_status=user_status_instance)
            news_record_instance.is_scraped = False

        return JsonResponse({'message': {'text': '설정이 완료되었습니다.'},
                             'keyboard': {'type': 'buttons',
                                          'buttons': first_button_list}
                             })

    elif is_feedback:
        print(content)
        print(feedback_list)
        return JsonResponse({'message': {'text': '피드백 메뉴 입니다.'},
                             'keyboard': {'type': 'buttons',
                                          'buttons': feedback_list}
                             })
    elif is_feedback_list:
        print(content)
        prev_select[user_key] = content
        return JsonResponse({'message': {'text': '자유롭게 입력해주세요'}})

    elif prev_select.get(user_key) in feedback_list:
        user_key, prev_select.get(user_key), content

        return JsonResponse({'message': {'text': '피드백이 완료되었습니다.'},
                             'keyboard': {'type': 'buttons',
                                          'buttons': first_button_list}
                             })

    elif is_latest_news:
        prev_select[user_key] = '최신 뉴스 보기'
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

    elif prev_select.get(user_key) == u'키워드로 검색':
        print('키워드로 검색')
        print(content)
        user_request[user_key] = get_news_by_id(engine.search_news_document(content))
        result_list = list(user_request[user_key].keys())
        print(result_list)
        del prev_select[user_key]

        if len(result_list) == 0:
            return JsonResponse({'message': {'text': '검색 결과가 없습니다.'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': first_button_list}
                                 })

        else:
            return JsonResponse({'message': {'text': '검색 결과 입니다'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': result_list}
                                 })

    elif content == u'맞춤형 뉴스 추천':
        print('맞춤형 뉴스 추천')
        user_key_list = user_info_manager.get_n_similar_user(user_key, 1)
        print(user_key_list)

        # user_based 로는 가장 유사한 유저 뽑아서 그 사람이 본 뉴스 뽑고
        try:
            news_id_list = user_info_manager.get_document_by_user_key(user_key_list[0])[0:5]
        except:
            news_id_list = []

        print(news_id_list)
        # page rank 는 이 사람이 가장 최근에 본 뉴스들 가지고 검색해서 보여주자
        user_status_object = UserStatus.objects.get(user_key=user_key)
        news_requirement = NewsRecord.objects.filter(
            user_status=user_status_object,
        ).order_by("-request_time")[:20]

        # 최종적으로 추려낸 news_id_list 여기서 이미 본건 빼보자

        news_id_list += engine.search_news_document(news_requirement.values_list('request_title', flat=True)[0])
        print(news_id_list)

        for i in news_id_list:
            if list(NewsRecord.objects.filter(user_status=user_status_object, request_news_id=i)) != 0:
                news_id_list.remove(i)
        news_id_list = list(set(news_id_list))
        print(news_id_list)

        user_request[user_key] = get_news_by_id(news_id_list)
        result_list = list(user_request[user_key].keys())
        print(result_list)
        return JsonResponse({'message': {'text': '추천뉴스 뉴스입니다.'},
                             'keyboard': {'type': 'buttons',
                                          'buttons': result_list}
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
            if prev_select.get(user_key) == '최근 본 뉴스' or prev_select.get(user_key) == '저장한 뉴스':
                return_list = add_index_of_list(list(user_request[user_key].keys()))
            elif prev_select.get(user_key) == '최신 뉴스 보기':
                return_list = list(user_request[user_key].keys())
                return_list += ['view more']
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
        print(news_select_button_list)
        return JsonResponse({'message': {'text': '어떤 검색을 원하시나요?'},
                             'keyboard': {'type': 'buttons',
                                          'buttons': news_select_button_list}
                             })
    elif is_news_keyword_search_select:
        prev_select[user_key] = '키워드로 검색'
        return JsonResponse({'message': {'text': '키워드를 입력해주세요'}})

    elif is_news_date_search_select:
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
        return1 = collections.OrderedDict(news_requirement.values_list('request_title', 'request_news_id'))
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
        return1 = collections.OrderedDict(news_requirement.values_list('request_title', 'request_news_id'))
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

        similar_news_id_list = engine.search_news_document(selected_news_title[user_key])
        similar_news_list = get_news_by_id(similar_news_id_list)

        # 여기 고쳐야함
        # 추천은 최신 뉴스 보기와 검색에만 있도록 하자
        # 여기 if 문에서 빼고 다른 분기로 편입
        # title 을 눌렀다는 것을 확인하기 위해서 user_request 외에 다른 변수에 저장하던지 하자
        user_request[user_key] = similar_news_list

        if prev_select.get(user_key) == '저장한 뉴스':
            return_button_list = maintain_remove_news_save_list
        elif prev_select.get(user_key) == '최근 본 뉴스':
            return_button_list = ['continue', 'stop']
        else:
            return_button_list = agree_disagree_news_save_list

        return_button_list = list(similar_news_list.keys()) + return_button_list

        print(return_button_list)
        return JsonResponse({'message': {"text": selected_news_title[user_key] + "\n————————————------\n"
                                                 + category.get(user_key) + ', ' + press.get(user_key) + ', ' + str(
            published_date) +
                                                 '\n—————---——---—————\n'
                                                 + text + "\n—————---———---————\n"
                                                 + url
                                         },
                             'keyboard': {'type': 'buttons',
                                          'buttons': return_button_list}
                             })

    elif is_save_news_title:
        if content == u'스크랩 하기':
            print(content)

            doc_id = str(user_request.get(user_key).get(selected_news_title[user_key]))

            news_scrap = NewsRecord.objects.get(request_news_id=doc_id)
            news_scrap.is_scraped = True
            news_scrap.save()

            if prev_select.get(user_key) == '저장한 뉴스' or prev_select.get(user_key) == '최신 뉴스 보기':
                return_button_list = ['continue', 'stop']
            else:
                return_button_list = end_of_service_list

            return JsonResponse({'message': {"text": "스크랩 하기 \n 저장하신 뉴스 정보는 일주일간 보관합니다"},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': return_button_list}
                                 })
        elif content == u'하지 않기':
            print(content)

            if prev_select.get(user_key) == '저장한 뉴스' or prev_select.get(user_key) == '최신 뉴스 보기':
                return_button_list = ['continue', 'stop']
            else:
                return_button_list = end_of_service_list

            return JsonResponse({'message': {'text': '뉴스를 스크랩 하지 않았습니다.'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': return_button_list}
                                 })
        elif content == u'유지하기':
            print(content)
            return_button_list = ['continue', 'stop']

            return JsonResponse({'message': {'text': '뉴스가 유지 되었습니다.'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': return_button_list}
                                 })
        elif content == u'삭제하기':
            print(content)
            doc_id = str(user_request.get(user_key).get(selected_news_title[user_key]))

            user_status_object = UserStatus.objects.get(user_key=user_key)
            news_scrap = NewsRecord.objects.filter(
                user_status=user_status_object,
                request_news_id=doc_id,
            )
            news_scrap.update(is_scraped=False)

            news_requirement = NewsRecord.objects.filter(
                user_status=user_status_object,
                is_scraped=True
            ).order_by("-request_time")[:20]

            user_request[user_key] = collections.OrderedDict(
                news_requirement.values_list('request_title', 'request_news_id'))
            print("renew_saved_news: " + str(user_request[user_key]))

            return_button_list = ['continue', 'stop']

            return JsonResponse({'message': {'text': '뉴스가 삭제 되었습니다.'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': return_button_list}
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
                {'message': {'text': '동의해주셔서 감사합니다. 원활한 맞춤형 추천, 이용자 통계를 위해 성별/나이/지역 정보를 수집합니다. 성별을 선택해주세요.'},
                 'keyboard': {'type': 'buttons',
                              'buttons': gender_list}
                 })

        else:
            print("동의하지 않습니다")
            button_list = ['동의합니다', '동의하지 않습니다']
            return JsonResponse({'message': {'text': '정보 수집에 동의하지 않으셨습니다. 다음에 다시 이용해주세요!'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': button_list}
                                 })

    elif is_in_gender:
        print('성별에 대한 답변을 한 상태' + str(content))
        user_info_gender[user_key] = content
        print(user_info_gender)
        print(birth_year_list)
        return JsonResponse({'message': {'text': '출생년도를 입력해주세요.'},
                             'keyboard': {'type': 'buttons',
                                          'buttons': birth_year_list}
                             })

    elif is_in_birth_year:
        print('생년에 대한 답변을 한 상태' + str(content))
        user_info_birth_year[user_key] = content
        print(user_info_birth_year)
        print(region_list)
        return JsonResponse({'message': {'text': '거주 지역을 입력해주세요.'},
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
                      "\n출생년도: " + str(user_info_birth_year[user_key]) + \
                      "\n지역: " + str(user_info_region[user_key])
        del user_info_gender[user_key]
        del user_info_region[user_key]
        del user_info_birth_year[user_key]
        print(show_result)
        intro = '“호외요”에서 최신순 뉴스 제공, 날짜/관심 분야/신문사별 뉴스 검색과 키워드 뉴스 검색 서비스를 이용하실 수 있습니다. 요약된 뉴스와 원문 링크가 함께 제공되며, ' \
                '최근 본 뉴스와 스크랩 기능을 통해 이전에 보셨던 뉴스를 최대 20개까지 다시 보실 수 있습니다. 또, 뉴스 이용 취향에 따라 맞춤형 뉴스를 큐레이팅해드리고 있습니다. \n\n' \
                '덤으로 나의 뉴스 이용 경향을 분석한 결과도 확인하실 수 있어요. \n\n' \
                '텍스트 입력창에 ‘설정’을 입력해서 개인 설정을 바꾸거나, ‘피드백’을 입력해서 건의사항이나 서비스 평가를 하실 수 있습니다. 그럼, 아직 요약 알고리즘이 개선 중이라 일부 뉴스의 ' \
                '경우 요약이 불완전할 수 있다는 점 양해 부탁드리며, 이제 본격적으로 서비스를 이용하러 가실까요!! '
        return JsonResponse({'message': {'text': show_result + '\n정보 수집이 모두 완료되었습니다. 감사합니다.\n' + intro},
                             'keyboard': {'type': 'buttons',
                                          'buttons': first_button_list}
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


def check_is_in_setting_list(content):
    if content in setting_list:
        return True
    else:
        return False


def check_is_in_feedback_list(content):
    if content in feedback_list:
        return True
    else:
        return False


def check_is_feedback(content):
    if content == u'피드백':
        return True
    else:
        return False


def check_is_setting(content):
    if content == u'설정':
        return True
    else:
        return False


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
    if content in ['동의합니다', '동의하지 않습니다']:
        return False
    elif content in gender_list:
        return False
    elif content in birth_year_list:
        return False
    elif content in region_list:
        return False
    elif len(UserStatus.objects.filter(user_key=user_key)) == 0:
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


def check_is_in_news_date_search(content):
    if content == u'날짜로 검색':
        return True
    else:
        return False


def check_is_in_news_keyword_search(content):
    if content == u'키워드로 검색':
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
    global prev_select

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
    try:
        del prev_select[user_key]
    except Exception as e:
        print('이전 선택이 저장 되지 않아 못 지움')

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
        ).order_by('-request_time').values_list('request_press', flat=True).distinct())
    except Exception as e:
        print(str(e))

    counter_press_list = Counter(return_press_list)

    result = []
    for i in counter_press_list:
        result.append(str(i) + ' (' + str(counter_press_list[i]) + ')')

    result.sort()
    result = ["--------------------"] + result

    additional_press_list = make_unique_list(additional_press_list)
    additional_press_list = additional_press_list[0:5]

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
