# -*- coding: utf-8 -*-

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from article.lists import year_list
from article import user_request_handler

handler = user_request_handler.UserRequestHandler()


@csrf_exempt
def message(request):
    global handler

    message = request.body.decode('utf-8')
    return_json_str = json.loads(message)
    content = return_json_str['content']
    user_key = return_json_str['user_key']

    if handler.check_is_in_year_list(user_key, content):
        if handler.is_full(user_key):
            return_document = handler.user_request.get(user_key)
            print(handler.user_request.get(user_key))
            if return_document is None:
                return JsonResponse({
                    'message': {'text': '선택이 모두 완료되었지만, 해당하는 기사가 없습니다.'},
                    'keyboard': {'type': 'buttons',
                                 'buttons': year_list
                                 }
                })
            else:
                result_list = list(return_document.get(user_key).values_list('title', flat=True))
                print(result_list)
                return JsonResponse({
                    'message': {'text': '선택이 모두 완료되었습니다. 관심있는 기사가 있으신가요?'},
                    'keyboard': {'type': 'buttons',
                                 'buttons': result_list
                                 }
                })
        else:
            print("[연도]아직 선택이 덜 되었습니다.")

            month_list = make_list('month', user_key)

            return JsonResponse({
                'message': {'text': "'연도'까지 선택이 완료 되었습니다! '월'을 선택해 주세요"},
                'keyboard': {'type': 'buttons',
                             'buttons': month_list
                             }
            })

    elif handler.check_is_in_month_list(user_key, content):
        if handler.is_full(user_key):
            return_document = handler.user_request.get(user_key)
            print(handler.user_request.get(user_key))
            if return_document is None:
                return JsonResponse({
                    'message': {'text': '선택이 모두 완료되었지만, 해당하는 기사가 없습니다.'},
                    'keyboard': {'type': 'buttons',
                                 'buttons': year_list
                                 }
                })
            else:
                result_list = list(return_document.get(user_key).values_list('title', flat=True))
                print(result_list)
                return JsonResponse({
                    'message': {'text': '선택이 모두 완료되었습니다. 관심있는 기사가 있으신가요?'},
                    'keyboard': {'type': 'buttons',
                                 'buttons': result_list
                                 }
                })

        else:
            print("[월]아직 선택이 덜 되었습니다.")

            day_list = make_list('day', user_key)

            return JsonResponse({
                'message': {'text': "'월'까지 선택이 완료 되었습니다! '일'을 선택해 주세요"},
                'keyboard': {'type': 'buttons',
                             'buttons': day_list
                             }
            })

    elif handler.check_is_in_day_list(user_key, content):
        if handler.is_full(user_key):
            return_document = handler.user_request.get(user_key)
            if return_document is None:
                return JsonResponse({
                    'message': {'text': '선택이 모두 완료되었지만, 해당하는 기사가 없습니다.'},
                    'keyboard': {'type': 'buttons',
                                 'buttons': year_list
                                 }
                })
            else:
                result_list = list(return_document.get(user_key).values_list('title', flat=True))
                print(result_list)
                return JsonResponse({
                    'message': {'text': '선택이 모두 완료되었습니다. 관심있는 기사가 있으신가요?'},
                    'keyboard': {'type': 'buttons',
                                 'buttons': result_list
                                 }
                })

        else:
            print("[일]아직 선택이 덜 되었습니다.")
            category_list = make_list('category', user_key)
            print(category_list)
            return JsonResponse({
                'message': {'text': "'일'까지 선택이 완료 되었습니다! '분야'를 선택해 주세요"},
                'keyboard': {'type': 'buttons',
                             'buttons': category_list
                             }
            })

    elif handler.check_is_in_category_list(user_key, content):
        print(handler.user_request.get(user_key))

        if handler.is_full(user_key):
            return_document = handler.user_request.get(user_key)
            if return_document is None:
                return JsonResponse({
                    'message': {'text': '선택이 모두 완료되었지만, 해당하는 기사가 없습니다.'},
                    'keyboard': {'type': 'buttons',
                                 'buttons': year_list
                                 }
                })
            else:
                result_list = list(return_document.get(user_key).values_list('title', flat=True))
                return JsonResponse({
                    'message': {'text': '선택이 모두 완료되었습니다. 관심있는 기사가 있으신가요?'},
                    'keyboard': {'type': 'buttons',
                                 'buttons': result_list
                                 }
                })

        else:
            print("[분야]아직 선택이 덜 되었습니다.")

            press_list = make_list('press', user_key)
            print("check_is_in_category" + str(press_list))
            return JsonResponse({
                'message': {'text': "'분야'까지 선택이 완료 되었습니다! '신문사'를 선택해 주세요"},
                'keyboard': {'type': 'buttons',
                             'buttons': press_list
                             }
            })

    elif handler.check_is_in_press_list(user_key, content):
        if handler.is_full(user_key):
            return_document = handler.user_request.get(user_key)
            print(handler.user_request.get(user_key))

            list(handler.user_request.get(user_key).values_list('title', flat=True))
            if return_document is None:
                return JsonResponse({
                    'message': {'text': '선택이 모두 완료되었지만, 해당하는 기사가 없습니다.'},
                    'keyboard': {'type': 'buttons',
                                 'buttons': year_list
                                 }
                })
            else:
                result_list = list(handler.user_request.get(user_key).values_list('title', flat=True))
                print("check_is_in_press" + str(result_list))
                return JsonResponse({
                    'message': {'text': '선택이 모두 완료되었습니다. 관심있는 기사가 있으신가요?'},
                    'keyboard': {'type': 'buttons',
                                 'buttons': result_list
                                 }
                })

        else:
            print("[신문사] 아직 선택이 덜 되었습니다.")

            handler.reset(user_key)

            return JsonResponse({
                'message': {'text': "중간에 뭔가 잘못되었나봐요 ㅜㅜ 다시 골라주세용 죄송합니다."},
                'keyboard': {'type': 'buttons',
                             'buttons': year_list
                             }
            })

    elif handler.check_is_news_title(user_key, content):
        title = handler.summary[user_key][0]
        text = handler.summary[user_key][1]
        url = handler.summary[user_key][2]

        del handler.summary[user_key]
        print(title)
        print(text)
        print(url)
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
                'buttons': year_list
            }
        })


def make_list(input_date, user_key):
    global handler
    if input_date == 'month':
        month_list = list(handler.politics_document.get(user_key).values_list('published_date', flat=True).distinct())
        month_list.extend(list(handler.society_document.get(user_key).values_list('published_date', flat=True).distinct()))
        month_list.extend(list(handler.economics_document.get(user_key).values_list('published_date', flat=True).distinct()))
        month_list.extend(list(handler.culture_living_document.get(user_key).values_list('published_date', flat=True).distinct()))
        month_list.extend(list(handler.it_science_document.get(user_key).values_list('published_date', flat=True).distinct()))
        month_list.extend(list(handler.world_document.get(user_key).values_list('published_date', flat=True).distinct()))
        new_month_list = []
        for i in month_list:
            new_month_list.append(i.month)
        month_list = list(set(new_month_list))
        return month_list

    elif input_date == 'day':
        day_list = list(handler.politics_document.get(user_key).values_list('published_date', flat=True).distinct())
        day_list.extend(
            list(handler.society_document.get(user_key).values_list('published_date', flat=True).distinct()))
        day_list.extend(
            list(handler.economics_document.get(user_key).values_list('published_date', flat=True).distinct()))
        day_list.extend(
            list(handler.culture_living_document.get(user_key).values_list('published_date', flat=True).distinct()))
        day_list.extend(
            list(handler.it_science_document.get(user_key).values_list('published_date', flat=True).distinct()))
        day_list.extend(
            list(handler.world_document.get(user_key).values_list('published_date', flat=True).distinct()))
        new_day_list = []
        for i in day_list:
            new_day_list.append(i.day)
        day_list = list(set(new_day_list))
        return day_list

    elif input_date == 'category':

        category_list = []
        if handler.politics_document.get(user_key).exists():
            category_list.append('정치')
        elif handler.economics_document.get(user_key).exists():
            category_list.append('경제')
        elif handler.society_document.get(user_key).exists():
            category_list.append('사회')
        elif handler.culture_living_document.get(user_key).exists():
            category_list.append('생활/문화')
        elif handler.world_document.get(user_key).exists():
            category_list.append('세계')
        elif handler.it_science_document.get(user_key).exists():
            category_list.append('IT/과학')

        return category_list

    elif input_date == 'press':
        press_list = list(handler.user_request.get(user_key).values_list('press', flat=True).distinct())
        press_list = list(set(press_list))

        return press_list
