import time

from django.http import (
    HttpRequest,
    JsonResponse,
    HttpResponseNotAllowed,
)
from lb.models import Submission, User
from django.forms.models import model_to_dict
from django.db.models import F
import json
from lb import utils
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.views.decorators.http import require_http_methods as method


def hello(req: HttpRequest):
    return JsonResponse({
        "code": 0,
        "msg": "hello"
    })


# TODO: Add HTTP method check
@method(["GET"])
def leaderboard(req: HttpRequest):
    return JsonResponse(
        utils.get_leaderboard(),
        safe=False,
    )


@method(["GET"])
def history(req: HttpRequest, username: str):
    # TODO: Complete `/history/<slug:username>` API
    try:
        res = Submission.objects.filter(user=username).order_by('time')
        return JsonResponse({
            {
                "score": ch.score,
                "subs": ch.subs,
                "tiem": ch.time
            } for ch in res
        })
    except:
        return JsonResponse({
            "code": -1
        })


@method(["POST"])
@csrf_exempt
def submit(req: HttpRequest):
    # TODO: Complete `/submit` API
    info: dict = json.loads(req.body)
    if not ("name" in info.keys() and "avatar" in info.keys() and "content" in info.keys()):
        return JsonResponse({
            "code": 1,
            "msg": "参数不全啊"
        })
    if len(info["name"]) > 255:
        return JsonResponse({
            "code": 1,
            "msg": "用户名太长了"
        })
    if len(info["avatar"]) > 1e5:
        return JsonResponse({
            "code": -1,
            "msg": "图像太大了"
        })
    if utils.judge(info["content"]):
        if not User.objects.get(username=info['name']):
            User.objects.create(username=info['name'], votes=0)
        Submission.objects.create(user=info['name'], avatar=info['avatar'], time=time.time(),
                                  score=utils.judge(info['content'])[0], subs=utils.judge(info['content'])[1])
        User.save()
        Submission.save()
        return JsonResponse({
            "code": 0,
            "msg": "提交成功",
            "data": {
                "leaderboard": utils.get_leaderboard()
            }
        })
    else:
        return JsonResponse({
            "code": -3,
            "msg": "提交内容非法呜呜"
        })


@method(["POST"])
@csrf_exempt
def vote(req: HttpRequest):
    if 'User-Agent' not in req.headers \
            or 'requests' in req.headers['User-Agent']:
        return JsonResponse({
            "code": -1
        })

    # TODO: Complete `/vote` API
    user = json.load(req.body)['user']
    if User.objects.get(user):
        User.objects.get(user).votes += 1
        User.save()
        return JsonResponse({
            "code": 0,
            "data": {
                "leaderboard": utils.get_leaderboard()
            }
        })
    else:
        return JsonResponse({
            "code": -1
        })
