# -*- coding: utf-8 -*-


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from crawler.getNews import *
from article.models import *
from article.lists import *
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

    is_press = check_is_in_presslist(content)
    is_year = check_is_in_yearlist(content)
    is_month = check_is_in_monthlist(content, user_key)
    is_day = check_is_in_daylist(content)
    is_category = check_is_in_categorylist(content)
    is_news_title = check_is_news_title(content, user_key)

    if content == u"신문사 고르기":
        return JsonResponse({
            'message': {
                'text': "신문사를 골라주세요!"
                },
            'keyboard': {
                'type': 'buttons',
                'buttons' : presslist
                }
            })
    elif content == u"날짜 고르기":
        return JsonResponse({
            'message': {
                'text': "날짜를 골라주세요!"
                },
            'keyboard': {
                'type': 'buttons',
                'buttons': yearlist
                }
            })
    elif content == u"분야 고르기":
        return JsonResponse({
            'message': {
                'text': "분야를 골라주세요!"
                },
            'keyboard': {
                'type': 'buttons',
                'buttons': categorylist
                }
            })
    elif is_press:
        press[user_key] = content
        print("here is isPress " + press[user_key])
        
        if is_Full(user_key):
            print("Press and Full")
            date = year[user_key]+"년 "+month[user_key]+"월 "+day[user_key]+"일"
            result = press[user_key] + ", " + date + ", " + category[user_key]
            rq = Requirement(user_key=user_key, press=press[user_key], date=date, category=category[user_key])
            rq.save()
            response = getNews(press[user_key], year[user_key], month[user_key], day[user_key], category[user_key])
            result_list = []
            for i in response.keys():
                result_list.append(response[i])

            print(result_list)
            user_request[user_key] = result_list

            del press[user_key]
            del category[user_key]
            del year[user_key]
            del month[user_key]
            del day[user_key]

            return JsonResponse({
                'message': {
                    'text': result+'선택이 모두 완료되었습니다. 관심있는 기사가 있으신가요?'
                    },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': result_list
                    }
                })
        else:
            result = press.get(user_key)
            if year.get(user_key) is not None:
                result += ", "
                result += year.get(user_key)
                result += "년"
            if month.get(user_key) is not None:
                result += month.get(user_key)
                result += "월 "
            if day.get(user_key) is not None:
                result += day.get(user_key)
                result += "일"
            if category.get(user_key) is not None:
                result += ", "
                result += category.get(user_key)
                
            return JsonResponse({
                'message': {
                    'text': result+" 선택이 완료 되었습니다! 날짜를 택해 보시겠어요?"
                    },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': yearlist
                    }
                })
    elif is_year:
        year[user_key] = content
        print("here is isYear " + year[user_key] + "년")
        
        if is_Full(user_key):
            print("Year and Full")
            date = year[user_key]+"년 "+month[user_key]+"월 "+day[user_key]+"일"
            result = press[user_key] + ", " + date + ", " + category[user_key]
            rq = Requirement(user_key=user_key, press=press[user_key], date=date, category=category[user_key])
            rq.save()
            response = getNews(press[user_key], year[user_key], month[user_key], day[user_key], category[user_key])
            result_list = []
            for i in response.keys():
                result_list.append(response[i])

            print(result_list)
            user_request[user_key] = result_list

            del press[user_key]
            del category[user_key]
            del year[user_key]
            del month[user_key]
            del day[user_key]

            return JsonResponse({
                'message': {
                    'text': result+'선택이 모두 완료되었습니다. 관심있는 기사가 있으신가요?'
                    },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': result_list
                    }
                })       
        else:
            return JsonResponse({
                'message': {
                    'text': year[user_key]+"년으로 선택이 완료 되었습니다. 몇월 인가요?"
                    },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': monthlist
                    }
            })   

    elif is_month:
        month[user_key] = content
        print("here is isMonth "+ month[user_key] +"월")
        
        if is_Full(user_key):
            print("Month and Full")
            date = year[user_key]+"년 "+month[user_key]+"월 "+day[user_key]+"일"
            result = press[user_key] + ", " + date + ", " + category[user_key]
            rq = Requirement(user_key=user_key, press=press[user_key], date=date, category=category[user_key])
            rq.save()
            response = getNews(press[user_key], year[user_key], month[user_key], day[user_key], category[user_key])
            result_list = []
            for i in response.keys():
                result_list.append(response[i])

            print(result_list)
            user_request[user_key] = result_list

            del press[user_key]
            del category[user_key]
            del year[user_key]
            del month[user_key]
            del day[user_key]

            return JsonResponse({
                'message': {
                    'text': result+'선택이 모두 완료되었습니다. 관심있는 기사가 있으신가요?'
                    },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': result_list
                    }
                })
        else:
            return JsonResponse({
                'message': {
                    'text': year[user_key]+"년 "+month[user_key]+" 월 선택이 완료 되었습니다! 며칠인가요?"
                    },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': daylist
                    }
            })   
    elif is_day:
        day[user_key] = content
        print("here is isDay " + day[user_key] + "일")
        
        if is_Full(user_key):
            print("Day and Full")
            date = year[user_key]+"년 "+month[user_key]+"월 "+day[user_key]+"일"
            result = press[user_key] + ", " + date + ", " + category[user_key]
            rq = Requirement(user_key=user_key, press=press[user_key], date=date, category=category[user_key])
            rq.save()
            response = getNews(press[user_key], year[user_key], month[user_key], day[user_key], category[user_key])
            result_list = []
            for i in response.keys():
                result_list.append(response[i])

            print(result_list)
            user_request[user_key] = result_list

            del press[user_key]
            del category[user_key]
            del year[user_key]
            del month[user_key]
            del day[user_key]

            return JsonResponse({
                'message': {
                    'text': result+'선택이 모두 완료되었습니다. 관심있는 기사가 있으신가요?'
                    },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': result_list
                    }
                })
        else:
            result = ""
            if press.get(user_key) is not None:
                result += press.get(user_key)
            if year.get(user_key) is not None:
                result += ", "
                result += year.get(user_key)
                result += "년"
            if month.get(user_key) is not None:
                result += ", "
                result += month.get(user_key)
                result += "월"
            if day.get(user_key) is not None:
                result += ", "
                result += day.get(user_key)
                result += "일"
            if category.get(user_key) is not None:
                result += ", "
                result += category.get(user_key)
            return JsonResponse({
                'message': {
                    'text': result+" 선택이 완료 되었습니다! 분야를 선택해 보시겠어요?"
                    },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': categorylist
                    }
            })   
    
    elif is_category:
        category[user_key] = content
        print("here is isCategory" + category[user_key])
        
        if is_Full(user_key):
            print("Category and Full")
            date = year[user_key]+"년 "+month[user_key]+"월 "+day[user_key]+"일"
            result = press[user_key] + ", " + date + ", " + category[user_key]
            rq = Requirement(user_key=user_key, press=press[user_key], date=date, category=category[user_key])
            rq.save()
            response = getNews(press[user_key], year[user_key], month[user_key], day[user_key], category[user_key])
            result_list = []
            for i in response.keys():
                result_list.append(response[i])

            print(result_list)
            user_request[user_key] = result_list

            del press[user_key]
            del category[user_key]
            del year[user_key]
            del month[user_key]
            del day[user_key]

            return JsonResponse({
                'message': {
                    'text': result+'선택이 모두 완료되었습니다. 관심있는 기사가 있으신가요?'
                    },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': result_list
                    }
                }) 
        else:
            result = ""
            if press.get(user_key) is not None:
                result += press.get(user_key)
            if year.get(user_key) is not None:
                result += ", "
                result += year.get(user_key)
                result += "년"
            if month.get(user_key) is not None:
                result += ", "
                result += month.get(user_key)
                result += "월"
            if day.get(user_key) is not None:
                result += ", "
                result += day.get(user_key)
                result += "일"
            if category.get(user_key) is not None:
                result += ", "
                result += category.get(user_key)
            
            return JsonResponse({
                'message': {
                    'text': result+" 선택이 완료 되었습니다! 다른것을 선택해 보시겠어요?"
                    },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': menulist
                    }
                })
    elif is_news_title:
        print(content)
        title, text, link = get_summary(content)

        del user_request[user_key]

        print(title)
        print(text)
        print(link)
        return JsonResponse({
            'message': {
                "text": "요청하신 뉴스 입니다.\n"+title+"\n"+text,
                'message_button': {
                    "label": "기사 바로가기",
                    "url": link
                }
            },
            'keyboard': {
                'type': 'buttons',
                'buttons': presslist
            }
        })

    else:
        print("정의되지 않은 구문")
        return JsonResponse({
            'message': {'text': '죄송합니다 정의되지 않은 응답입니다.'},
            'keyboard': {
                'type': 'buttons',
                'buttons': menulist
                }
            })


# 신문사 이름중 하나인지 확인
def check_is_in_presslist(content):
    if content in presslist:
        return True
    else:
        return False


# 날짜 목록중 하나인지 체크 -- 임시방편이라 수정해야함
def check_is_in_yearlist(content):
    if content in yearlist:
        return True
    else:
        return False


# 월 목록중 하나인지 체크
def check_is_in_monthlist(content,user_key):
    global month
    if month.get(user_key) is not None:
        return False
    elif content in monthlist:
        return True
    else:
        return False


# 일 목록중 하나인지 체크
def check_is_in_daylist(content):
    if content in daylist:
        return True
    else:
        return False


# 카테고리 중 하나인지 체크
def check_is_in_categorylist(content):
    if content in categorylist:
        return True
    else:
        return False


# 뉴스를 요청하는 것인지확인
def check_is_news_title(content, user_key):
    if user_request.get(user_key) is None:
        return False
    elif content in user_request.get(user_key):
        return True
    else:
        return False


# 전부다 선택했는지 확인
def is_Full(user_key):
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

