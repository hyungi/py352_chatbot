# -*- coding: utf-8 -*-


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from crawler.get_news import get_news, get_summary
from article.models import Requirement, NewsRequirement
from article.lists import press_list, category_list, date_list

'''
/article/answers.py

'''
date = {}
category = {}
press = {}
user_request = {}

@csrf_exempt
def message(request):
    global date
    global category
    global press
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
    is_date = check_is_in_date_list(content)
    is_category = check_is_in_category_list(content)
    is_news_title = check_is_news_title(content, user_key)

    if is_date:
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
            return JsonResponse({
                'message': {'text': str(return1) + "여기까지 선택이 완료 되었습니다! 다른것을 선택해 주세요"},
                'keyboard': {'type': 'buttons',
                             'buttons': press_list
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
            print("result_list")
            print(result_list)

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


# 신문사 이름중 하나인지 확인
def check_is_in_press_list(content):
    if content in press_list:
        return True
    else:
        return False


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
    del press[user_key]

    try:
        del user_request[user_key]
    except Exception as e:
        print("뉴스가 없어서 저장을 못했는데 어떻게 지우냐 멍청아!")


# global result 라는 변수 하나만을 선언해서 result = {'encrypted_user_key':{'press':'조선일보','year':'2018','category':'정치'}} 등으로 처리해보자
