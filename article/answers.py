# -*- coding: utf-8 -*-
import re

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from crawler.get_news import get_news, get_summary, get_news_by_id, get_category_by_doc_id, \
    get_press_by_doc_id_category, get_latest_news
from article.models import Requirement, UserStatus, NewsRecord, FeedBack
from article.lists import press_list, date_list, category_list, gender_list, birth_year_list, region_list, \
    first_button_list, agree_disagree_news_save_list, end_of_service_list, maintain_remove_news_save_list, \
    news_select_button_list, feedback_list, setting_list, news_recomm_service_agree_disagree, stars_list
from crawler.models import *
from collections import Counter
from article.user_info_class import news_record, user_status, user_information_manager
from article.save_user_info import save_user_status
from django.utils import timezone
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
recommend_news = {}
selected_news_title = {}
news_title_list = {}
prev_select = {}
feedback_select ={}

user_info_gender = {}
user_info_birth_year = {}
user_info_region = {}
page_number = 0

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
user_info_manager = user_information_manager(path=os.path.join(BASE_DIR, 'info_matrix.txt'))

dtm_path = os.path.join(BASE_DIR, 'dtm.txt')
matrix_path = os.path.join(BASE_DIR, 'vctr.txt')
path = {'dtm_path': dtm_path, 'matrix_path': matrix_path}
engine = search_engine_manager(**path)


@csrf_exempt
def message(request):
    global date
    global category
    global press
    global recommend_news
    global user_request
    global selected_news_title
    global news_title_list
    global prev_select
    global feedback_select

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

    is_feedback_first_depth = check_is_in_feedback_first_depth(content)
    is_feedback_second_depth = check_is_in_feedback_second_depth(content, user_key)
    is_feedback_third_depth = check_is_in_feedback_third_depth(user_key)
    is_feedback = check_is_feedback(content)

    is_setting_list = check_is_in_setting_list(content)
    is_setting = check_is_setting(content)

    is_news_recomm_service_setting = check_news_recomm_service_setting(content)

    if is_first_use:
        print("UserStatus 가 없는 경우에 적용함")
        button_list = ['동의합니다', '동의하지 않습니다']
        return JsonResponse({'message': {'text': '안녕하세요. 최신 뉴스를 요약해주는 “호외요”입니다. \n' +
                                                 '최신 뉴스는 물론, 날짜/관심 분야/언론사별로 원하는 뉴스를 검색하고 스크랩할 수 있는 서비스입니다. \n' +
                                                 '원활한 서비스 제공을 위해 사용자의 기본 정보를 수집하고 있습니다. 수집한 정보는 맞춤형 뉴스 추천, 이용자 통계 서비스 제공에 사용됩니다. 개인정보 제공에 동의하시나요? \n'
                                         },
                             'keyboard': {'type': 'buttons',
                                          'buttons': button_list}
                             })
    elif is_end_of_service:
        if content == '메인 메뉴로':
            reset_globals(user_key)
            return JsonResponse({'message': {'text': '메인 메뉴로 돌아갑니다.'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': first_button_list}
                                 })
        elif content == '다시 검색하기':
            if prev_select.get(user_key) == '키워드로 검색':
                prev_select[user_key] = '키워드로 검색'
                return JsonResponse({'message': {'text': '키워드를 입력해주세요'}})

            elif prev_select.get(user_key) == u'날짜로 검색':
                return JsonResponse({'message': {'text': '날짜를 골라주세요'},
                                     'keyboard': {'type': 'buttons',
                                                  'buttons': date_list + ['메인 메뉴로']}
                                     })
        else:
            if prev_select.get(user_key) == '최근 본 뉴스' or prev_select.get(user_key) == '저장한 뉴스' or prev_select.get(user_key) == '맞춤형 뉴스 큐레이팅':
                return_list = add_index_of_list(list(user_request[user_key].keys()))
                return_list += ['메인 메뉴로']
            elif prev_select.get(user_key) == '최신 뉴스 보기':
                return_list = list(user_request[user_key].keys())
                return_list += ['더 보기', '메인 메뉴로']
            else:
                return_list = list(user_request[user_key].keys()) + end_of_service_list

            print(return_list)
            if len(return_list) == 0:
                return JsonResponse({'message': {'text': '저장된 뉴스가 없습니다'},
                                     'keyboard': {'type': 'buttons',
                                                  'buttons': first_button_list}
                                     })
            else:
                return JsonResponse({'message': {'text': '목록으로 돌아갑니다.'},
                                     'keyboard': {'type': 'buttons',
                                                  'buttons': return_list}
                                     })

    elif content == u'뒤로 가기':
        if prev_select[user_key] == '카테고리':
            try:
                del category[user_key]
            except:
                print('카테고리 선택 안해서 못지움')
            if date[user_key] in date_list:
                prev_select[user_key] = '정해준 날짜 고름'
            else:
                prev_select[user_key] = '직접 입력'
            return JsonResponse({'message': {'text': "카테고리를 선택해 주세요"},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': category_list + ['뒤로 가기']}
                                 })

        elif prev_select[user_key] == '정해준 날짜 고름':
            try:
                del date[user_key]
            except:
                print('날짜 선택 안해서 못지움')
            prev_select[user_key] = '날짜로 검색'
            return JsonResponse({'message': {'text': "날짜를 선택해 주세요"},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': date_list + ['뒤로 가기']}
                                 })

        elif prev_select[user_key] == '직접 입력':
            return JsonResponse({'message': {'text': '원하는 날짜를 직접 입력해주세요'}})

        elif prev_select[user_key] == '날짜로 검색':
            prev_select[user_key] = '뉴스 검색'
            return JsonResponse({'message': {'text': "어떤 검색을 원하시나요?"},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': news_select_button_list}
                                 })
    elif is_news_recomm_service_setting:
        if content == u'서비스를 이용하겠습니다':
            user_status_instance = UserStatus.objects.get(user_key=user_key)
            user_status_instance.recommend_service = True
            user_status_instance.save()
            return_message = '뉴스 추천 서비스 이용 설정이 완료 되었습니다.'

        else:
            user_status_instance = UserStatus.objects.get(user_key=user_key)
            user_status_instance.recommend_service = False
            user_status_instance.save()
            return_message = '뉴스 추천 서비스 이용안함 설정이 완료 되었습니다.'

        return JsonResponse({'message': {'text': return_message},
                             'keyboard': {'type': 'buttons',
                                          'buttons': first_button_list}
                             })

    elif is_setting:
        print(content)
        print(setting_list)
        return JsonResponse({'message': {'text': '설정 메뉴 입니다.'},
                             'keyboard': {'type': 'buttons',
                                          'buttons': setting_list + ['메인 메뉴로']}
                             })

    elif is_setting_list:
        print(content)
        print(first_button_list)

        if content == setting_list[0]:
            return JsonResponse({'message': {'text': '뉴스 추천 서비스 설정메뉴 입니다.'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': news_recomm_service_agree_disagree + ['메인 메뉴로']}
                                 })

        else:
            reset_is_scraped(user_key)
            return JsonResponse({'message': {'text': '저장한 뉴스 초기화가 완료되었습니다.'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': first_button_list}
                                 })

    elif is_feedback:
        print(content)
        print(feedback_list)
        return JsonResponse({'message': {'text': '피드백 메뉴 입니다'},
                             'keyboard': {'type': 'buttons',
                                          'buttons': feedback_list + ['메인 메뉴로']}
                             })
    elif is_feedback_first_depth:
        if content == u'이용 후기':
            prev_select[user_key] = content
            print('별점 요청')
            return JsonResponse({'message': {'text': '서비스 만족도가 어느정도 인가요?(5점 만점)'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': stars_list}
                                 })

        elif content == u'오류 레포트':
            prev_select[user_key] = content
            print('오류 발생 지점 확인')

            return JsonResponse({'message': {'text': '어떤 서비스에서 오류가 발생 하셨나요?'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': first_button_list}
                                 })
        else:
            print('건의사항 메뉴임')
            prev_select[user_key] = content
            feedback_select[user_key] = content
            return JsonResponse({'message': {'text': '건의 사항을 자유롭게 입력해주세요'}})

    elif is_feedback_second_depth:
        print(content)
        feedback_select[user_key] = content
        return JsonResponse({'message': {'text': '자유롭게 입력해주세요'}})

    elif is_feedback_third_depth:
        print(content)

        feedback_instance = FeedBack(
            user_status=UserStatus.objects.get(user_key=user_key),
            feedback_type=prev_select.get(user_key),
            second_depth=feedback_select.get(user_key),
            feedback_content=content,
        )
        feedback_instance.save()

        reset_globals(user_key)

        return JsonResponse({'message': {'text': '피드백이 완료되었습니다.'},
                             'keyboard': {'type': 'buttons',
                                          'buttons': first_button_list}
                             })

    elif prev_select.get(user_key) in feedback_list:
        feedback_instance = FeedBack(
            user_status=UserStatus.objects.get(user_key=user_key),
            feedback_type=prev_select.get(user_key),
            feedback_content=content,
        )
        feedback_instance.save()

        print(user_key, prev_select.get(user_key), content)
        reset_globals(user_key)
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
        return_list += ['더 보기', '메인 메뉴로']
        print(return_list)
        return JsonResponse({'message': {'text': '최신뉴스 목록 ' + str(page_number) + '페이지 입니다'},
                             'keyboard': {'type': 'buttons',
                                          'buttons': return_list}
                             })

    elif content == u'맞춤형 뉴스 큐레이팅':
        prev_select[user_key] = '맞춤형 뉴스 큐레이팅'
        print(content)
        user_key_list = user_info_manager.get_n_similar_user(user_key, 1)
        print(user_key_list)

        # user_based 로는 가장 유사한 유저 뽑아서 그 사람이 본 뉴스 뽑고
        try:
            news_id_list = user_info_manager.get_document_by_user_key(user_key_list[0])[0:5]
        except:
            news_id_list = []

        # page rank 는 이 사람이 가장 최근에 본 뉴스들 가지고 검색해서 보여주자
        user_status_object = UserStatus.objects.get(user_key=user_key)
        news_requirement = NewsRecord.objects.filter(
            user_status=user_status_object,
        ).order_by("-request_time")[:3]

        # 최종적으로 추려낸 news_id_list 여기서 이미 본건 빼보자
        print(timezone.now())
        news_requirement_list = list(news_requirement.values_list('request_title', flat=True))

        for i in news_requirement_list:
            news_id_list += engine.search_news_document(i)

        print(timezone.now())
        news_id_list = list(set(news_id_list))

        news_record_instance = NewsRecord.objects.filter(user_status=UserStatus.objects.get(user_key=user_key))

        for i in news_record_instance:
            if i.request_news_id in news_id_list:
                news_id_list.remove(i.request_news_id)
                print('이미 본 뉴스라 삭제')

        news_id_list = list(set(news_id_list))

        news_id_list = news_id_list[0:20]

        print(news_id_list)

        user_request[user_key] = get_news_by_id(news_id_list)
        result_list = list(user_request[user_key].keys()) + ['메인 메뉴로']
        print(result_list)
        return JsonResponse({'message': {'text': '추천뉴스 뉴스입니다.'},
                             'keyboard': {'type': 'buttons',
                                          'buttons': result_list}
                             })

    elif is_tutorial:
        print('tutorial page')
        usage_guide = '안녕하세요. “호외요”를 이용해주셔서 감사합니다.\n-간단한 설정은 “설정”을 타이핑하셔서 조정하실 수 있습니다.\n-이용후기, 오류 레포트, 건의사항 등의 피드백은 “피드백”을 타이핑하셔서 보내실 수 있습니다.' \
                      '\n\n1. 최신 뉴스 보기\n최신 뉴스를 바로 보실 수 있는 메뉴입니다. \n최근에 본 뉴스는 메인 메뉴의 ‘최근 본 뉴스’에 저장되고, 별도로 스크랩하여 메인 메뉴의 ‘저장한 뉴스’에서 다시 확인하실 수 있습니다. 뉴스 조회 후 관련된 뉴스를 추천해드립니다.' \
                      '\n(최신 뉴스는 매일 07:00, 15:00, 22:00에 업데이트됩니다.)\n(뉴스 추천 여부는 ‘설정’을 타이핑하시면 설정이 가능합니다.)' \
                      '\n\n2. 맞춤형 뉴스 큐레이팅\n사용자의 뉴스 사용 경향(언론사/카테고리, 평소 조회한 뉴스 등)에 따라 맞춤형 뉴스를 추천해드립니다.' \
                      '\n\n3. 뉴스 검색' \
                      '\n-날짜로 검색 : 보고자 하는 뉴스의 날짜/카테고리/언론사에 따라 원하는 뉴스를 검색하실 수 있습니다.\n-키워드로 검색 : 원하는 내용의 뉴스를 키워드로 검색하실 수 있습니다.' \
                      '\n\n4. 최근 본 뉴스' \
                      '\n최근에 조회한 뉴스 목록을 최대 20개까지 유지하고 확인하실 수 있습니다.' \
                      '\n\n5. 저장한 뉴스' \
                      '\n뉴스 서비스를 이용하시다가 스크랩한 뉴스를 확인하실 수 있습니다. 각 뉴스를 클릭하시면 내용 조회와 유지, 삭제가 가능하며, ‘설정’을 타이핑하시면 전체 목록을 삭제하실 수 있습니다.' \
                      '\n\n6. 뉴스 이용 통계' \
                      '\n회원님의 평소 뉴스 이용 경향(언론사/카테고리, 관심 있게 본 뉴스)을 시각화하여 확인하실 수 있습니다.\n(연령대별 통계는 현재 서비스 준비 중입니다.)'
        print(usage_guide)
        return JsonResponse({'message': {'text': usage_guide},
                             'keyboard': {'type': 'buttons',
                                          'buttons': first_button_list}
                             })

    elif is_news_select:
        print('news_select_page')
        print(news_select_button_list)
        prev_select[user_key] = '뉴스 검색'
        return JsonResponse({'message': {'text': '어떤 검색을 원하시나요?'},
                             'keyboard': {'type': 'buttons',
                                          'buttons': news_select_button_list}
                             })
    elif is_news_keyword_search_select:
        prev_select[user_key] = '키워드로 검색'
        return JsonResponse({'message': {'text': '키워드를 입력해주세요'}})

    elif is_news_date_search_select:
        prev_select[user_key] = '날짜로 검색'
        return JsonResponse({'message': {'text': '날짜를 골라주세요'},
                             'keyboard': {'type': 'buttons',
                                          'buttons': date_list + ['뒤로 가기']}
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
                                              'buttons': result_list + ['메인 메뉴로']}
                                 })
        else:
            print('최근에 본 뉴스가 없을 경우')
            return JsonResponse({'message': {'text': '저장하신 뉴스가 없습니다'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': first_button_list}
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
                                              'buttons': result_list + ['메인 메뉴로']}
                                 })
        else:
            print('최근에 본 뉴스가 없을 경우')
            return JsonResponse({'message': {'text': '최근에 보신 뉴스가 없습니다'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': first_button_list}
                                 })

    elif is_date:
        reset_globals(user_key)
        prev_select[user_key] = '정해준 날짜 고름'
        if content == u'직접 입력':
            prev_select[user_key] = '직접 입력'
            print('닐짜 직접 입력')
            return JsonResponse({'message': {'text': '원하는 날짜를 2018-03-01 의 형태로 직접 입력해주세요'}})

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
                                              'buttons': category_list + ['뒤로 가기']}
                                 })

    elif prev_select.get(user_key) == u'직접 입력':
        print('직접 입력한 날짜: ' + str(content))
        datetime_format = re.compile(r"\d{4}-\d{2}-\d{2}")
        if datetime_format.search(content) is not None:
            date[user_key] = content
            prev_select[user_key] = ""
            return JsonResponse({'message': {'text': str(content) + "분야를 선택해 주세요"},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': category_list + ['뒤로 가기']}
                                 })

        else:
            return JsonResponse({'message': {'text': '날짜를 잘못 입력 하셨습니다. 2018-03-01 의 형태로 다시입력해 주세요'}})

    elif is_category:
        category[user_key] = content
        print("selected category is" + category[user_key])
        return1 = handle_request(user_key)
        prev_select[user_key] = '카테고리'

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
                return JsonResponse({'message': {'text': '날짜와 카테고리에 맞는 언론사가 없습니다. 다시 골라 주세요'},
                                     'keyboard': {'type': 'buttons',
                                                  'buttons': date_list}
                                     })

            return JsonResponse({'message': {'text': str(return1) + "다른것을 선택해 주세요"},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': return_press_list + ['뒤로 가기']}
                                 })

    elif is_press:
        if content == '--------------------':
            print('구분자를 선택한 상황임')

            return_press_list = make_press_list(category[user_key], user_key)
            print(return_press_list)

            return JsonResponse({'message': {'text': '언론사를 다시 골라주세요'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': return_press_list + ['뒤로 가기']}
                                 })

        prev_select[user_key] = '신문사'

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
            prev_select[user_key] = '날짜로 검색'
            return JsonResponse({'message': {'text': '선택이 모두 완료되었습니다. 관심있는 기사가 있으신가요?'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': result_list + ['다시 검색하기', '메인 메뉴로']}
                                 })
        else:
            return JsonResponse({'message': {'text': str(return1) + "날짜를 선택해 주세요"},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': date_list}
                                 })

    elif is_news_title:
        print(content)
        doc_id = ""

        separator = ' '
        rest = ''
        try:
            rest = content.split(separator, 1)[1]
            print(rest)
        except Exception as e:
            print(e)

        try:
            if content in user_request.get(user_key).keys():
                doc_id = str(user_request.get(user_key).get(content))
        except:
            print("content is not in user_request")

        try:
            if rest in user_request.get(user_key).keys():
                doc_id = str(user_request.get(user_key).get(rest))
        except:
            print("rest is not in user_request")

        try:
            if content in recommend_news.get(user_key).keys():
                doc_id = str(recommend_news.get(user_key).get(content))
        except:
            print("content is not in recommend_news")

        try:
            if rest in recommend_news.get(user_key).keys():
                doc_id = str(recommend_news.get(user_key).get(rest))
        except:
            print("rest is not in recommend_news")

        print("in_is_news_title: " + doc_id)
        category[user_key] = get_category_by_doc_id(doc_id)
        press[user_key] = get_press_by_doc_id_category(doc_id, category[user_key])

        selected_news_title[user_key], text, url, published_date = get_summary(doc_id, category[user_key])
        print(category.get(user_key))
        print(press.get(user_key))

        if len(NewsRecord.objects.filter(user_status__exact=UserStatus.objects.get(user_key=user_key), request_news_id=doc_id)) == 0:
            news_info = {"document_id": doc_id, "press": press.get(user_key),
                         "category": category.get(user_key), "title": selected_news_title[user_key],
                         "request_time": timezone.now().strftime("%Y-%m-%d %H:%M")}

            news_record_instance = news_record(**news_info)
            user_info_manager.update_user_record(user_key, news_record_instance)
        else:
            news_record_update = NewsRecord.objects.get(
                user_status__exact=UserStatus.objects.get(user_key=user_key),
                request_news_id=doc_id,
            )
            news_record_update.request_time = timezone.now().strftime("%Y-%m-%d %H:%M")
            news_record_update.save()

        print(selected_news_title[user_key])
        print(text)
        print(url)
        print(published_date)

        if prev_select.get(user_key) == '저장한 뉴스':
            return_button_list = maintain_remove_news_save_list
        elif prev_select.get(user_key) == '최근 본 뉴스':
            return_button_list = ['목록으로', '메인 메뉴로']
        else:
            return_button_list = agree_disagree_news_save_list
            # return_button_list = list(similar_news_list.keys()) + return_button_list

        if UserStatus.objects.get(user_key=user_key).recommend_service is True:
            similar_news_id_list = engine.search_news_document(selected_news_title[user_key])

            news_record_instance = NewsRecord.objects.filter(user_status=UserStatus.objects.get(user_key=user_key))

            for i in news_record_instance:
                if i.request_news_id in similar_news_id_list:
                    print('이미 본 뉴스라 삭제함')
                    similar_news_id_list.remove(i.request_news_id)

            similar_news_list = get_news_by_id(similar_news_id_list)
            recommend_news[user_key] = similar_news_list
            print("추천 뉴스 목록: " + str(recommend_news[user_key]))

        print(return_button_list)
        return JsonResponse({'message': {"text": selected_news_title[user_key] + "\n————————————------\n"
                                                 + category.get(user_key) + ', ' + press.get(user_key) + ', '
                                                 + str(published_date) + '\n—————---——---—————\n'
                                                 + text + "\n—————---———---————\n"
                                                 + url
                                         },
                             'keyboard': {'type': 'buttons',
                                          'buttons': return_button_list}
                             })

    elif is_save_news_title:
        # recommend_news[user_key] 내부의 리스트가 매번 새로운 뉴스를 선택할 때마다 새롭게 갱신이 되는데, 추천 하는 과정에서 발생한 뉴스는
        # 새롭게 다른 뉴스를 추천하는 리스트로 갱신 되면서 recommend_news[user_key] 내부에서 사라지게 된다.
        print(selected_news_title[user_key])

        print("======저장할지 말지 물은 뒤의 상태")
        print(user_request.get(user_key))
        print(recommend_news.get(user_key))

        if content == u'스크랩 하기':
            print(content)

            user_status_instance = UserStatus.objects.get(user_key=user_key)
            news_scrap = NewsRecord.objects.get(
                user_status__exact=user_status_instance,
                request_title=selected_news_title[user_key],
            )
            news_scrap.is_scraped = True
            news_scrap.save()

            if prev_select.get(user_key) == '저장한 뉴스':
                return_button_list = ['목록으로', '메인 메뉴로']
            elif prev_select.get(user_key) == '최신 뉴스 보기' or prev_select.get(user_key) == '맞춤형 뉴스 큐레이팅':
                if recommend_news.get(user_key) is not None:
                    return_button_list = list(recommend_news.get(user_key).keys()) + ['목록으로', '메인 메뉴로']
                else:
                    return_button_list = ['목록으로', '메인 메뉴로']
            else:
                if recommend_news.get(user_key) is not None:
                    return_button_list = list(recommend_news.get(user_key).keys()) + end_of_service_list
                else:
                    return_button_list = end_of_service_list

            return JsonResponse({'message': {"text": "스크랩 하기 \n 저장하신 뉴스 정보는 일주일간 보관합니다"},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': return_button_list}
                                 })

        elif content == u'스크랩 하지 않음':
            print(content)

            if prev_select.get(user_key) == '저장한 뉴스':
                return_button_list = ['목록으로', '메인 메뉴로']
            elif prev_select.get(user_key) == '최신 뉴스 보기' or prev_select.get(user_key) == '맞춤형 뉴스 큐레이팅':
                if recommend_news.get(user_key) is not None:
                    return_button_list = list(recommend_news.get(user_key).keys()) + ['목록으로', '메인 메뉴로']
                else:
                    return_button_list = ['목록으로', '메인 메뉴로']
            else:
                if recommend_news.get(user_key) is not None:
                    return_button_list = list(recommend_news.get(user_key).keys()) + end_of_service_list
                else:
                    return_button_list = end_of_service_list

            return JsonResponse({'message': {'text': '뉴스를 스크랩 하지 않았습니다.'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': return_button_list}
                                 })
        elif content == u'유지하기':
            print(content)
            return_button_list = ['목록으로', '메인 메뉴로']

            return JsonResponse({'message': {'text': '뉴스가 유지 되었습니다.'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': return_button_list}
                                 })
        elif content == u'삭제하기':
            print(content)
            doc_id = str(user_request.get(user_key).get(selected_news_title[user_key]))

            if doc_id == 'None':
                doc_id = str(recommend_news.get(user_key).get(selected_news_title[user_key]))

            print(doc_id)

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

            return_button_list = ['목록으로', '메인 메뉴로']

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
        intro = '“호외요”에서 최신순 뉴스 제공, 날짜/관심 분야/언론사별 뉴스 검색과 키워드 뉴스 검색 서비스를 이용하실 수 있습니다. 요약된 뉴스와 원문 링크가 함께 제공되며, ' \
                '최근 본 뉴스와 스크랩 기능을 통해 이전에 보셨던 뉴스를 최대 20개까지 다시 보실 수 있습니다. 또, 뉴스 이용 취향에 따라 맞춤형 뉴스를 큐레이팅해드리고 있습니다. \n\n' \
                '덤으로 나의 뉴스 이용 경향을 분석한 결과도 확인하실 수 있어요. \n\n' \
                '텍스트 입력창에 ‘설정’을 입력해서 개인 설정을 바꾸거나, ‘피드백’을 입력해서 건의사항이나 서비스 평가를 하실 수 있습니다. 그럼, 아직 요약 알고리즘이 개선 중이라 일부 뉴스의 ' \
                '경우 요약이 불완전할 수 있다는 점 양해 부탁드리며, 이제 본격적으로 서비스를 이용하러 가실까요!! '
        return JsonResponse({'message': {'text': show_result + '\n정보 수집이 모두 완료되었습니다. 감사합니다.\n' + intro},
                             'keyboard': {'type': 'buttons',
                                          'buttons': first_button_list}
                             })

    elif prev_select.get(user_key) == u'키워드로 검색':
        print('키워드로 검색')
        print(content)
        user_request[user_key] = get_news_by_id(engine.search_news_document(content))
        result_list = list(user_request[user_key].keys())
        print(result_list)
        if len(result_list) == 0:
            reset_globals(user_key)
            return JsonResponse({'message': {'text': '검색 결과가 없습니다.'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': first_button_list}
                                 })

        else:
            result_list += ['다시 검색하기', '메인 메뉴로']
            return JsonResponse({'message': {'text': '검색 결과 입니다'},
                                 'keyboard': {'type': 'buttons',
                                              'buttons': result_list}
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


def check_is_in_feedback_third_depth(user_key):
    global feedback_select
    if feedback_select.get(user_key) in stars_list or feedback_select.get(user_key) in first_button_list or prev_select.get(user_key) == u'건의사항':
        return True
    else:
        return False


def check_is_in_feedback_second_depth(content, user_key):
    global prev_select
    if prev_select.get(user_key) in feedback_list[0:2] and (content in stars_list or content in first_button_list):
        return True
    else:
        return False


def check_is_in_feedback_first_depth(content):
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
    if content == u'최신 뉴스 보기' or content == u'더 보기':
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
    global recommend_news
    separator = ' '
    rest = ''
    try:
        rest = content.split(separator, 1)[1]
        print(rest)
    except Exception as e:
        print(e)

    if user_request.get(user_key) is None and recommend_news.get(user_key) is None:
        return False
    else:
        print(user_request.get(user_key))
        try:
            if content in user_request.get(user_key).keys():
                return True
        except:
            print("")
        try:
            if rest in user_request.get(user_key).keys():
                return True
        except:
            print("")
        try:
            if content in recommend_news.get(user_key).keys():
                return True
        except:
            print("")

        try:
            if rest in recommend_news.get(user_key).keys():
                return True
        except:
            print("")

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
    global recommend_news
    global feedback_select

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
    try:
        del feedback_select[user_key]
    except Exception as e:
        print('피드백 이전에 저장 되지 않아 못지움')

    page_number = 0

    try:
        del recommend_news[user_key]
    except Exception as e:
        print('비슷한 뉴스 추천이 저장 되어 있지 않아 못지움')


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


def reset_is_scraped(user_key):
    user_status_instance = UserStatus.objects.get(user_key=user_key)
    news_record_instance = NewsRecord.objects.filter(user_status=user_status_instance)

    for i in news_record_instance:
        news_record_object = NewsRecord.objects.get(user_status=user_status_instance, request_news_id=i.request_news_id)
        news_record_object.is_scraped = False
        news_record_object.save()


def check_news_recomm_service_setting(content):
    if content in news_recomm_service_agree_disagree:
        return True
    else:
        return False
