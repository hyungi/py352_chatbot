# -*- coding: utf-8 -*-

from django.http import JsonResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
import json
from . import lists


# 고객의 요청 정보를 담을 객체 선언을 여기다 하자!
# request_list > answer.py 라는 걸 만들어서 여기다가 객체를 던져주고 요약한 것을 보내도록 하자
def keyboard(request):
    '''
    :param 카톡플친 API를 통해 넘어온 /keyboard request
    :return 카톡 플친 API를 적용할 때 필수적으로 요청하는 구성 요건으로
    json 값을 넘겨주기 위해 JsonResponse을 사용한다.
    '''

    return JsonResponse({
        'type': 'buttons',
        'buttons': lists.presslist
    })


@csrf_exempt
def add_friend(request):
    if request.method == "POST":
        message = ((request.body).decode('utf-8'))
        return_json_str = json.loads(message)
        user_key = return_json_str['user_key']
        # 튜플 생성
        return JsonResponse({"result": "done"})
    else:
        return HttpResponseNotFound


@csrf_exempt
def del_friend(request, user_key):
    if request.method == "DELETE":
        # 만들어둔 튜플 삭제
        return JsonResponse({"result": "done"})
    else:
        return HttpResponseNotFound

