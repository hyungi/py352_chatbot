# -*- coding: utf-8 -*-

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from article.lists import date_list
from article import user_request_handler

handler = user_request_handler.UserRequestHandler()


@csrf_exempt
def message(request):
    global handler

    message = request.body.decode('utf-8')
    return_json_str = json.loads(message)
    content = return_json_str['content']
    user_key = return_json_str['user_key']

    is_date = handler.check_is_in_date_list(user_key, content)
    is_category = handler.check_is_in_category_list(user_key, content)
    is_press = handler.check_is_in_press_list(user_key, content)
    is_news_title = handler.check_is_news_title(user_key, content)
    is_full = handler.is_full(user_key)

    if is_date:
        print("is_date")
        handler.do_query(user_key, content)
        print(handler.user_request.get(user_key))

        if is_full:
            return_document = handler.user_request.get(user_key)
            if return_document is None:
                handler.reset(user_key)
                return JsonResponse({
                    'message': {'text': '선택이 모두 완료되었지만, 해당하는 기사가 없습니다.'},
                    'keyboard': {'type': 'buttons',
                                 'buttons': date_list
                                 }
                })
            else:
                result_list = list(sorted(handler.user_request.get(user_key), key=lambda doc: doc.published_date, reverse=True).title)[0:10]
                return JsonResponse({
                    'message': {'text': '선택이 모두 완료되었습니다. 관심있는 기사가 있으신가요?'},
                    'keyboard': {'type': 'buttons',
                                 'buttons': result_list
                                 }
                })
        else:
            category_list = make_list('category', user_key)
            print("date is selected and category_list: " + str(category_list))
            return JsonResponse({
                'message': {'text': "'날짜'까지 선택이 완료 되었습니다! '신문사'를 선택해 주세요"},
                'keyboard': {'type': 'buttons',
                             'buttons': category_list
                             }
            })

    elif is_category:
        print("is_category")
        print(handler.user_request.get(user_key))
        handler.do_query(user_key, content)

        if is_full:
            if handler.user_request.get(user_key) is None:
                handler.reset(user_key)
                return JsonResponse({
                    'message': {'text': '선택이 모두 완료되었지만, 해당하는 기사가 없습니다.'},
                    'keyboard': {'type': 'buttons',
                                 'buttons': date_list
                                 }
                })
            else:
                result_list = list(sorted(handler.user_request.get(user_key), key=lambda doc: doc.published_date, reverse=True))[0:10]
                return JsonResponse({
                    'message': {'text': '선택이 모두 완료되었습니다. 관심있는 기사가 있으신가요?'},
                    'keyboard': {'type': 'buttons',
                                 'buttons': result_list
                                 }
                })

        else:
            press_list = make_list('press', user_key)
            print("category is selected and press_list: " + str(press_list))
            return JsonResponse({
                'message': {'text': "'분야'까지 선택이 완료 되었습니다! '신문사'를 선택해 주세요"},
                'keyboard': {'type': 'buttons',
                             'buttons': press_list
                             }
            })

    elif is_press:
        handler.do_query(user_key, content)
        print(handler.user_request.get(user_key))

        if is_full:
            if handler.user_request.get(user_key) is None:
                handler.reset(user_key)
                return JsonResponse({
                    'message': {'text': '선택이 모두 완료되었지만, 해당하는 기사가 없습니다.'},
                    'keyboard': {'type': 'buttons',
                                 'buttons': date_list
                                 }
                })
            else:
                result_list = list(sorted(handler.user_request.get(user_key), key=lambda doc: doc.published_date, reverse=True))[0:10]
                return_list = []
                for i in result_list:
                    return_list.extend(i.title)
                print("all selected: " + str(return_list))
                return JsonResponse({
                    'message': {'text': '선택이 모두 완료되었습니다. 관심있는 기사가 있으신가요?'},
                    'keyboard': {'type': 'buttons',
                                 'buttons': return_list
                                 }
                })

        else:
            print("[신문사] 아직 선택이 덜 되었습니다.")

            handler.reset(user_key)

            return JsonResponse({
                'message': {'text': "중간에 뭔가 잘못되었나봐요 ㅜㅜ 다시 골라주세용 죄송합니다."},
                'keyboard': {'type': 'buttons',
                             'buttons': date_list
                             }
            })

    elif is_news_title:
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
                'buttons': date_list
            }
        })


def make_list(input_date, user_key):
    global handler

    if input_date == 'category':
        print('make_category_list')
        category_list = []
        if handler.politics_document.get(user_key).exists():
            category_list.append('정치')
        if handler.economics_document.get(user_key).exists():
            category_list.append('경제')
        if handler.society_document.get(user_key).exists():
            category_list.append('사회')
        if handler.culture_living_document.get(user_key).exists():
            category_list.append('생활/문화')
        if handler.world_document.get(user_key).exists():
            category_list.append('세계')
        if handler.it_science_document.get(user_key).exists():
            category_list.append('IT/과학')

        return category_list

    elif input_date == 'press':
        press_list = list(handler.user_request.get(user_key).values_list('press', flat=True).distinct())
        press_list = list(set(press_list))

        return press_list
