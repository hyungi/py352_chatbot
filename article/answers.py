# -*- coding: utf-8 -*-


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from crawler.get_news import get_news, get_summary
from article.models import Requirement, NewsRequirement
from article.lists import press_list, category_list, year_list, month_list, day_list, menu_list

'''
/article/answer.py

'''
press = {}
year = {}
month = {}
day = {}
category = {}
user_request = {}


@csrf_exempt
def message(request):
    global press
    global year
    global month
    global day
    global category
    global user_request

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
    is_year = check_is_in_year_list(content)
    is_month = check_is_in_month_list(content, user_key)
    is_day = check_is_in_day_list(content)
    is_category = check_is_in_category_list(content)
    is_news_title = check_is_news_title(content, user_key)

    if content == u"신문사 고르기":
        return JsonResponse({
            'message': {'text': "신문사를 골라주세요!"},
            'keyboard': {
                'type': 'buttons',
                'buttons': press_list
            }
        })
    elif content == u"날짜 고르기":
        return JsonResponse({
            'message': {'text': "날짜를 골라주세요!"},
            'keyboard': {'type': 'buttons',
                         'buttons': year_list
                         }
        })
    elif content == u"분야 고르기":
        return JsonResponse({
            'message': {'text': "분야를 골라주세요!"},
            'keyboard': {'type': 'buttons',
                         'buttons': category_list
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
                                 'buttons': press_list
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
            return JsonResponse({
                'message': {'text': str(return1) + "여기까지 선택이 완료 되었습니다! 다른것을 선택해 주세요"},
                'keyboard': {'type': 'buttons',
                             'buttons': year_list
                             }
            })

    elif is_year:
        year[user_key] = content
        print("selected year is " + year[user_key] + "년")
        return1  = handle_request(user_key)
        if isinstance(return1, dict):
            if return1.get("none") is not None:
                reset_globals(user_key)
                return JsonResponse({
                    'message': {'text': '선택이 모두 완료되었지만, 해당하는 기사가 없습니다.'},
                    'keyboard': {'type': 'buttons',
                                 'buttons': press_list
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
            return JsonResponse({
                'message': {'text': str(return1) + "여기까지 선택이 완료 되었습니다! 다른것을 선택해 주세요"},
                'keyboard': {'type': 'buttons',
                             'buttons': month_list
                             }
            })

    elif is_month:
        month[user_key] = content
        print("selected month is " + month[user_key] + "월")
        return1 = handle_request(user_key)
        if isinstance(return1, dict):
            if return1.get("none") is not None:
                reset_globals(user_key)
                return JsonResponse({
                    'message': {'text': '선택이 모두 완료되었지만, 해당하는 기사가 없습니다.'},
                    'keyboard': {'type': 'buttons',
                                 'buttons': press_list
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
            return JsonResponse({
                'message': {'text': str(return1) + "여기까지 선택이 완료 되었습니다! 다른것을 선택해 주세요"},
                'keyboard': {'type': 'buttons',
                             'buttons': day_list
                             }
            })

    elif is_day:
        day[user_key] = content
        print("selected day is " + day[user_key] + "일")
        return1 = handle_request(user_key)
        if isinstance(return1, dict):
            if return1.get("none") is not None:
                reset_globals(user_key)
                return JsonResponse({
                    'message': {'text': '선택이 모두 완료되었지만, 해당하는 기사가 없습니다.'},
                    'keyboard': {'type': 'buttons',
                                 'buttons': press_list
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
            return JsonResponse({
                'message': {'text': str(return1) + "여기까지 선택이 완료 되었습니다! 다른것을 선택해 주세요"},
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
                                 'buttons': press_list
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
            return JsonResponse({
                'message': {'text': str(return1) + "여기까지 선택이 완료 되었습니다! 다른것을 선택해 주세요"},
                'keyboard': {'type': 'buttons',
                             'buttons': press_list
                             }
            })

    elif is_news_title:
        title, text, link = get_summary(str(user_request.get(user_key).get(content)), category[user_key])

        news_requirement = NewsRequirement(
            user_key=user_key,
            asked_news_title=title,
        )
        news_requirement.save()

        reset_globals(user_key)

        print(title)
        print(text)
        print(link)
        return JsonResponse({
            'message': {
                "text": "요청하신 뉴스 입니다.\n" + title + "\n" + text,
                'message_button': {
                    "label": "기사 바로가기",
                    "url": link
                }
            },
            'keyboard': {
                'type': 'buttons',
                'buttons': press_list
            }
        })

    else:
        print("정의되지 않은 구문")
        return JsonResponse({
            'message': {'text': '죄송합니다 정의되지 않은 응답입니다.'},
            'keyboard': {
                'type': 'buttons',
                'buttons': press_list
            }
        })


# 신문사 이름중 하나인지 확인
def check_is_in_press_list(content):
    if content in press_list:
        return True
    else:
        return False


# 날짜 목록중 하나인지 체크 -- 임시방편이라 수정해야함
def check_is_in_year_list(content):
    if content in year_list:
        return True
    else:
        return False


# 월 목록중 하나인지 체크
def check_is_in_month_list(content, user_key):
    global month
    if month.get(user_key) is not None:
        return False
    elif content in month_list:
        return True
    else:
        return False


# 일 목록중 하나인지 체크
def check_is_in_day_list(content):
    if content in day_list:
        return True
    else:
        return False


# 카테고리 중 하나인지 체크
def check_is_in_category_list(content):
    if content in category_list:
        return True
    else:
        return False


# 뉴스를 요청하는 것인지확인
def check_is_news_title(content, user_key):
    global user_request

    if user_request.get(user_key) is None:
        return False
    else:
        if content in user_request.get(user_key).keys():
            return True
        else:
            return False


# 전부다 선택했는지 확인
def is_full(user_key):
    global press
    global year
    global month
    global day
    global category

    if press.get(user_key) is None:
        return False
    elif year.get(user_key) is None:
        return False
    elif month.get(user_key) is None:
        return False
    elif day.get(user_key) is None:
        return False
    elif category.get(user_key) is None:
        return False
    else:
        return True


# 고객 요청 처리 간소화
@csrf_exempt
def handle_request(user_key):
    global press
    global category
    global year
    global month
    global day

    if is_full(user_key):
        print("is_full")
        date = year[user_key] + "년 " + month[user_key] + "월 " + day[user_key] + "일"
        save_request = Requirement(user_key=user_key, press=press[user_key], date=date, category=category[user_key])
        save_request.save()
        response = get_news(press[user_key], year[user_key], month[user_key], day[user_key], category[user_key])
        print(response)

        return response

    else:
        print_result = []

        if category.get(user_key) is not None:
            print_result.append("[" + category.get(user_key) + "]")

        elif day.get(user_key) is not None:
            print_result.append(day.get(user_key) + "일 ")

        elif month.get(user_key) is not None:
            print_result.append(month.get(user_key) + "월 ")

        elif year.get(user_key) is not None:
            print_result.append(year.get(user_key) + "년 ")

        elif press.get(user_key) is not None:
            print_result.append("[" + press.get(user_key) + "] ")

        return print_result


def reset_globals(user_key):
    global press
    global year
    global month
    global day
    global category
    global user_request

    del press[user_key]
    del year[user_key]
    del month[user_key]
    del day[user_key]
    del category[user_key]
    try:
        del user_request[user_key]
    except Exception as e:
        print("뉴스가 없어서 저장을 못했는데 어떻게 지우냐 멍청아!")


# global result 라는 변수 하나만을 선언해서 result = {'encrypted_user_key':{'press':'조선일보','year':'2018','category':'정치'}} 등으로 처리해보자
