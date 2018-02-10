# -*- coding: utf-8 -*-

from django.http import JsonResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
import json
from .lists import date_list


# 고객의 요청 정보를 담을 객체 선언을 여기다 하자!
# request_list > answer.py 라는 걸 만들어서 여기다가 객체를 던져주고 요약한 것을 보내도록 하자
def keyboard(request):
    '''
    :param 카톡플친 API를 통해 넘어온 /keyboard request
    :return 카톡 플친 API를 적용할 때 필수적으로 요청하는 구성 요건으로
    json 값을 넘겨주기 위해 JsonResponse을 사용한다.
    '''
    first_button_list = ['사용방법 익히기', '뉴스 선택하기', '최근에 본 뉴스 확인하기']
    print(first_button_list)
    return JsonResponse({
        'type': 'buttons',
        'buttons': first_button_list
    })


@csrf_exempt
def add_friend(request):
    if request.method == "POST":
        message = request.body.decode('utf-8')
        return_json_str = json.loads(message)
        user_key = return_json_str['user_key']
        # 튜플 생성
        print("친구 추가시 보이는 화면")
        button_list = ['동의합니다', '동의하지 않습니다']
        return JsonResponse({'message': {'text': '첫 안내 문구'},
                             'keyboard': {'type': 'buttons',
                                          'buttons': button_list}
                             })
    else:
        return HttpResponseNotFound


@csrf_exempt
def del_friend(request, user_key):
    if request.method == "DELETE":
        # 만들어둔 튜플 삭제
        print("친구 삭제시 보이는 화면")
        return JsonResponse({"result": "done"})
    else:
        return HttpResponseNotFound


@csrf_exempt
def exit_chatroom(request, user_key):
    if request.method == "DELETE":
        print("채팅방을 나가면 보이는 화면")
        return JsonResponse({"result": "chat_room_out"})
    else:
        return HttpResponseNotFound
