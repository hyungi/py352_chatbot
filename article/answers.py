# -*- coding: utf-8 -*-


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from crawler.get_news import get_news, get_summary
from article.models import Requirement, NewsRequirement, UserStatus
from article.lists import press_list, date_list, category_list, gender_list, birth_year_list, job_list, region_list
from django.utils import timezone
from crawler.models import *
from collections import Counter

'''
/article/answers.py

'''
date = {}
category = {}
press = {}
user_request = {}

user_info = {}


@csrf_exempt
def message(request):
    global date
    global category
    global press
    global user_request
    global user_info

    '''
    :param 고객이 버튼을 눌렀을 경우 작동하는 함수로아래와 같은 정보가 전달된다.
    user_key: reqest.body.user_key, //user_key
    type: reqest.body.type,         //메시지 타입
    content: reqest.body.content    //메시지 내용
    :return JsonResponse를 통해 message 와 keyboard(optional)가 반환된다.
    '''
    message = request.body.decode('utf-8')
    return_json_str = json.loads(message)
    content = return_json_str['content']
    user_key = return_json_str['user_key']

    is_press = check_is_in_press_list(content)
    is_date = check_is_in_date_list(content)
    is_category = check_is_in_category_list(content)
    is_news_title = check_is_news_title(content, user_key)
    agree_flag1, agree_flag2 = check_is_agree_or_disagree(content)
    is_in_gender = check_is_in_gender_list(content)
    is_in_birth_year = check_is_in_birth_year_list(content)
    is_in_job_list = check_is_in_job_list(content)
    is_in_region_list = check_is_in_region_list(content)
    is_tutorial = content == '사용방법 익히기'
    is_news_select = content == '뉴스 선택하기'
    is_recent_news = content == '최근에 본 뉴스 확인하기'

    if is_tutorial:
        print('tutorial page')
        button_list = ['동의합니다', '동의하지 않습니다']

        return JsonResponse({'message': {'text': '첫 안내 문구'},
                             'keyboard': {'type': 'buttons',
                                          'buttons': button_list}
                             })

    elif is_news_select:
        print('news_select_page')

        return JsonResponse({'message': {'text': '우선 날짜부터 골라주세요!'},
                             'keyboard': {'type': 'buttons',
                                          'buttons': date_list}
                             })

    elif is_recent_news:
        print('is_recent_news')

        return JsonResponse({'message': {'text': '우선 날짜부터 골라주세요!'},
                             'keyboard': {'type': 'buttons',
                                          'buttons': date_list}
                             })

    elif is_date:
        date[user_key] = content
        print("selected day is " + date[user_key] + "일")
        return1 = handle_request(user_key)
        if isinstance(return1, dict):
            if return1.get("none") is not None:
                reset_globals(user_key)
                return JsonResponse({
                    'message': {'text': '선택이 모두 완료되었지만, 해당하는 기사가 없습니다.'},
                    'keyboard': {'type': 'buttons',
                                 'buttons': date_list
                                 }
                })

            result_list = []
            for i in return1.keys():
                result_list.append(return1[i])

            print(result_list)
            user_request[user_key] = result_list

            return JsonResponse({
                'message': {'text': '선택이 모두 완료되었습니다. 관심있는 기사가 있으신가요?'},
                'keyboard': {'type': 'buttons',
                             'buttons': result_list
                             }
            })
        else:
            print(category_list)
            return JsonResponse({
                'message': {'text': str(return1) + "여기까지 선택이 완료 되었습니다! 분야를 선택해 주세요"},
                'keyboard': {'type': 'buttons',
                             'buttons': category_list
                             }
            })

    elif is_category:
        category[user_key] = content
        print("selected category is" + category[user_key])
        return1 = handle_request(user_key)

        if isinstance(return1, dict):
            print("is_full and is_category")
            if return1.get("none") is not None:
                reset_globals(user_key)
                return JsonResponse({
                    'message': {'text': '선택이 모두 완료되었지만, 해당하는 기사가 없습니다.'},
                    'keyboard': {'type': 'buttons',
                                 'buttons': date_list
                                 }
                })

            result_list = []
            for i in return1.keys():
                result_list.append(i)

            print(result_list)
            user_request[user_key] = return1
            print(user_request[user_key])
            return JsonResponse({
                'message': {'text': '선택이 모두 완료되었습니다. 관심있는 기사가 있으신가요?'},
                'keyboard': {'type': 'buttons',
                             'buttons': result_list
                             }
            })
        else:
            return_press_list = make_press_list(content, user_key)
            print(return_press_list)

            if len(return_press_list) is 0:
                reset_globals(user_key)
                return JsonResponse({
                    'message': {'text': '날짜와 카테고리에 맞는 신문사가 없습니다. 다시 골라 주세요'},
                    'keyboard': {'type': 'buttons',
                                 'buttons': date_list
                                 }
                })

            return JsonResponse({
                'message': {'text': str(return1) + "여기까지 선택이 완료 되었습니다! 다른것을 선택해 주세요"},
                'keyboard': {'type': 'buttons',
                             'buttons': return_press_list
                             }
            })

    elif is_press:
        press[user_key] = content
        print("selected press is " + press[user_key])
        return1 = handle_request(user_key)

        if isinstance(return1, dict):
            if return1.get("none") is not None:
                reset_globals(user_key)
                return JsonResponse({
                    'message': {'text': '선택이 모두 완료되었지만, 해당하는 기사가 없습니다.'},
                    'keyboard': {'type': 'buttons',
                                 'buttons': date_list
                                 }
                })

            result_list = list(return1.keys())

            user_request[user_key] = return1

            return JsonResponse({
                'message': {'text': '선택이 모두 완료되었습니다. 관심있는 기사가 있으신가요?'},
                'keyboard': {'type': 'buttons',
                             'buttons': result_list
                             }
            })
        else:
            return JsonResponse({
                'message': {'text': str(return1) + "여기까지 선택이 완료 되었습니다! 날짜를 선택해 주세요"},
                'keyboard': {'type': 'buttons',
                             'buttons': date_list
                             }
            })

    elif is_news_title:
        title, text, url = get_summary(str(user_request.get(user_key).get(content)), category[user_key])

        print(text)
        print(url)

        news_requirement = NewsRequirement(
            user_key=user_key,
            request_news_title=title,
            request_news_id=str(user_request.get(user_key).get(content)),
        )
        news_requirement.save()

        reset_globals(user_key)

        return JsonResponse({
            'message': {
                "text": "요청하신 뉴스 입니다.\n" + title + "\n" + text,
                'message_button': {
                    "label": "기사 바로가기",
                    "url": url
                }
            },
            'keyboard': {
                'type': 'buttons',
                'buttons': date_list
            }
        })

    elif agree_flag1:
        print("최초 개인 정보 수집에 대한 답변입니다.")
        if agree_flag2:
            print("동의합니다.")
            return JsonResponse({
                'message': {'text': '동의해 주셔서 감사합니다. 원활한 서비스 제공을 위해 성별/나이/직업/지역에 대한 기본적인 정보수집을 진행하겠습니다.\n성별을 선택해주세요.'},
                'keyboard': {
                    'type': 'buttons',
                    'buttons': gender_list
                }
            })

        else:
            print("동의하지 않습니다.")
            return JsonResponse({
                'message': {'text': '확인해 주셔서 감사합니다.\n[[기본 안내문구]]'},
                'keyboard': {
                    'type': 'buttons',
                    'buttons': date_list
                }
            })

    elif is_in_gender:
        print('성별에 대한 답변을 한 상태' + str(content))
        user_info[user_key] = {'gender': content}
        print(user_info)
        return JsonResponse({
            'message': {'text': content + '라고 답변을 해주셌네요! 감사합니다. 출생년도를 입력해 주시겠어요?'},
            'keyboard': {
                'type': 'buttons',
                'buttons': birth_year_list
            }
        })

    elif is_in_birth_year:
        print('생년에 대한 답변을 한 상태' + str(content))
        user_info[user_key] = {'birth_year': content}
        print(user_info)
        return JsonResponse({
            'message': {'text': content + '라고 답변을 해주셨네요! 감사합니다. 직업을 입력해 주시겠어요?'},
            'keyboard': {
                'type': 'buttons',
                'buttons': job_list
            }
        })

    elif is_in_job_list:
        print('직업에 대한 답변을 한 상태' + str(content))
        user_info[user_key] = {'job': content}
        print(user_info)
        return JsonResponse({
            'message': {'text': content + '라고 답변을 해 주셨네요! 감사합니다. 마지막으로 지역을 입력해 주시겠어요?'},
            'keyboard': {
                'type': 'buttons',
                'buttons': region_list
            }
        })

    elif is_in_region_list:
        print('지역 답변까지 완료를 한 상태' + str(content))
        user_info[user_key] = {'region': content}
        print(user_info)
        # user_status = UserStatus(
        #     user_key=user_key,
        #     gender=user_info[user_key]['gender'],
        #     birth_year=user_info[user_key]['birth_year'],
        #     location=user_info[user_key]['region'],
        # )
        # user_status.save()

        show_result = "성별: " + str(user_info[user_key]['gender']) + \
                      "\n생년: " + str(user_info[user_key]['birth_year']) + \
                      "\n지역: " + str(user_info[user_key]['region'])
        del user_info[user_key]

        return JsonResponse({
            'message': {'text': show_result + '라고 답변을 해주셨네요! 정보 수집이 모두 완료되었습니다. 감사합니다.\n[[기본안내문구]]'},
            'keyboard': {
                'type': 'buttons',
                'buttons': date_list
            }
        })

    else:
        print("정의되지 않은 구문")
        reset_globals(user_key)

        return JsonResponse({
            'message': {'text': '죄송합니다 정의되지 않은 응답입니다.'},
            'keyboard': {
                'type': 'buttons',
                'buttons': date_list
            }
        })


# 지역을 선택한 상황인가
def check_is_in_region_list(content):
    if content in region_list:
        return True
    else:
        return False


# 직업을 선택한 상황인가
def check_is_in_job_list(content):
    if content in job_list:
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
def check_is_agree_or_disagree(content):
    if content == '동의합니다':
        return True, True
    elif content == '동의하지 않습니다':
        return True, False
    else:
        return False, False


# 날짜 목록중 하나인지 체크 -- 임시방편이라 수정해야함
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
    if content in press_list:
        return True
    else:
        return False


# 뉴스를 요청하는 것인지확인
def check_is_news_title(content, user_key):
    global user_request

    if user_request.get(user_key) is None:
        return False
    else:
        print(user_request.get(user_key))
        if content in user_request.get(user_key).keys():
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
        rq_date = date[user_key][0:4] + "년 " + date[user_key][6:7] + "월 " + date[user_key][9:10] + "일"
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

    del date[user_key]
    del category[user_key]
    try:
        del press[user_key]
    except Exception as e:
        print("신문사 아직 안골라서 못지움")

    try:
        del user_request[user_key]
    except Exception as e:
        print("뉴스가 없어서 저장을 못했는데 어떻게 지우냐 멍청아!")


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

    print(return_press_list)

    if NewsRequirement.objects.filter(user_key=user_key).exists():
        additional_press_list = Requirement.objects.filter(user_key=user_key).order_by('request_date').values_list(
            'press', flat=True)[:10]

    print(additional_press_list)
    for i in range(len(additional_press_list)):
        print(additional_press_list[i])
        if additional_press_list[i] in return_press_list:
            return_press_list = [additional_press_list[i]] + return_press_list

    counter_press_list = Counter(return_press_list)
    print(counter_press_list)
    result = []
    for i in counter_press_list:
        result.append(str(i) + ' (' + str(counter_press_list[i]) + ')')

    # 다른 신문사 보기 기능 추가 >> 원래 보던 신문사가 아닌 신문사는 따로 관리해서 보여주기.

    return result
