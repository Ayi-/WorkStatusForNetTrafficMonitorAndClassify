# coding=utf-8
from __future__ import print_function

import uuid
from calendar import timegm
import datetime

import jwt
from django.conf import settings
from django.contrib.auth import _get_user_session_key, _get_backends, SESSION_KEY, HASH_SESSION_KEY, \
    BACKEND_SESSION_KEY, \
    REDIRECT_FIELD_NAME
from django.contrib.auth import user_logged_out
from django.contrib.auth.decorators import user_passes_test
from django.middleware.csrf import rotate_token
from django.utils.crypto import constant_time_compare
from django.utils.translation import LANGUAGE_SESSION_KEY
from rest_framework import authentication
from rest_framework import exceptions
from rest_framework.compat import set_rollback
from rest_framework.response import Response
from rest_framework.views import exception_handler

import dashboard.models

# 分类种类
# categoryList=[u'IT', u'购物', u'军事', u'编程', u'娱乐', u'游戏', u'闲逛', u'搜索', u'生活', u'学术']
# 处理状态
statusList = [(0, u'未处理'), (1, u'已处理')]
# 记录状态
recordList = [(0, u'未记录'), (1, u'已记录'), (2, u'已存在')]


class DashBoardBackend(object):
    def authenticate(self, username=None, password=None):
        try:
            user = dashboard.models.User.objects.get(user_name=username)
            if user:
                localAuth = dashboard.models.LocalAuth.objects.get(user_id=user.pk)
                if localAuth and localAuth.check_password(password):
                    return user
        except dashboard.models.User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            user = dashboard.models.User.objects.get(id=user_id)
            return user
        except dashboard.models.User.DoesNotExist:
            return None

    def has_perm(self, user_obj, perm, obj=None):
        return False


def login(request, user, backend=None):
    """
    Persist a user id and a backend in the request. This way a user doesn't
    have to reauthenticate on every request. Note that data set during
    the anonymous session is retained when the user logs in.
    """
    session_auth_hash = ''
    if user is None:
        user = request.user
    if hasattr(user, 'get_session_auth_hash'):
        session_auth_hash = user.get_session_auth_hash()

    if SESSION_KEY in request.session:
        if _get_user_session_key(request) != user.pk or (
                    session_auth_hash and
                    not constant_time_compare(request.session.get(HASH_SESSION_KEY, ''), session_auth_hash)):
            # To avoid reusing another user's session, create a new, empty
            # session if the existing session corresponds to a different
            # authenticated user.
            request.session.flush()
    else:
        request.session.cycle_key()

    try:
        backend = backend or user.backend
    except AttributeError:
        backends = _get_backends(return_tuples=True)
        if len(backends) == 1:
            _, backend = backends[0]
        else:
            raise ValueError(
                'You have multiple authentication backends configured and '
                'therefore must provide the `backend` argument or set the '
                '`backend` attribute on the user.'
            )

    request.session[SESSION_KEY] = user._meta.pk.value_to_string(user)
    request.session[BACKEND_SESSION_KEY] = backend
    request.session[HASH_SESSION_KEY] = session_auth_hash
    if hasattr(request, 'user'):
        request.user = user
    rotate_token(request)
    # user_logged_in.send(sender=user.__class__, request=request, user=user)


def logout(request):
    """
    Removes the authenticated user's ID from the request and flushes their
    session data.
    """
    # Dispatch the signal before the user is logged out so the receivers have a
    # chance to find out *who* logged out.
    user = getattr(request, 'user', None)
    if hasattr(user, 'is_authenticated') and not user.is_authenticated:
        user = None
    user_logged_out.send(sender=user.__class__, request=request, user=user)

    # remember language choice saved to session
    language = request.session.get(LANGUAGE_SESSION_KEY)

    request.session.flush()

    if language is not None:
        request.session[LANGUAGE_SESSION_KEY] = language

    if hasattr(request, 'user'):
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()


def login_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='dashboardlogin'):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', '')
        e = exceptions.AuthenticationFailed()
        result = {'status': 'error'}
        e.detail = result
        if token:

            try:
                payload = jwt.decode(token, key=settings.SECRET_KEY)
                user = dashboard.models.User.objects.get(id=payload.get('user_id', 0))
            except dashboard.models.User.DoesNotExist:
                result['result'] = u'用户不存在'
                raise e
            except jwt.ExpiredSignatureError:
                result['result'] = u'Token已过期'
                raise e
            except jwt.DecodeError:
                result['result'] = u'非法Token'
                raise e
            except Exception:
                result['result'] = u'非法请求'
                raise e
            return (user, None)


# def custom_exception_handler(exc, context):
#     # Call REST framework's default exception handler first,
#     # to get the standard error response.
#     response = exception_handler(exc, context)
#     if isinstance(exc, exceptions.AuthenticationFailed):
#         data=data = {'detail': exc.detail}
#         set_rollback()
#         return Response(data, status=exc.status_code, headers=headers)
#     # Now add the HTTP status code to the response.
#     if response is not None:
#         response.data['status_code'] = response.status_code
#
#     return response
import pytz

shanghai = pytz.timezone('Asia/Shanghai')


def getShangHaiDateTimeFromTimestamp(tsp):
    """
    从timestamp转化成datetime，并且设置时区为上海
    :param tsp:
    :return:
    """
    global shanghai
    return datetime.datetime.fromtimestamp(tsp, shanghai)


def getShangHaiDateTimeFromTimestampWithStr(tsp):
    """
    从timestamp转化成datetime，并且设置时区为上海
    :param tsp:
    :return:
    """
    try:
        return getShangHaiDateTimeFromTimestamp(tsp).strftime('%Y/%m/%d %H:%M:%S')
    except:
        return None


def keyForGroupByDatetimeHour(dt):
    """
    以每小时分组
    :param time:
    :return:
    """
    return getShangHaiDateTimeFromTimestamp(dt.timestamp).replace(minute=0, second=0, microsecond=0)


def countGroupByCategoryWithTimeGroup(timeGroup):
    """
    根据时间段分类并计数
    :param data:
    :return:
    """

    categoryList = dashboard.models.CategoryTitle.objects.values_list('word')
    result = {}
    for item in categoryList:
        result[item[0]] = []
    for item in timeGroup:
        itemDatetime = getShangHaiDateTimeFromTimestamp(item[0].timestamp).replace(minute=0, second=0,
                                                                                   microsecond=0).strftime(
            "%Y/%m/%d %H:%M:%S")
        for k in result.keys():
            result[k].append([itemDatetime, count(item, lambda x: x.category == k)])
    return result


def countGroupByCategoryWithFullGroup(fullGroup):
    """
    在某一时间段内进行分类计数
    :param data:
    :return:
    """

    categoryList = dashboard.models.CategoryTitle.objects.values_list('word')
    result = {}
    for item in categoryList:
        result[item[0]] = 0
    for k in result.keys():
        result[k] = count(fullGroup, lambda x: x.category == k)
    return result


def getTipsForPieData(pieData):
    """
    根据饼图数据提出建议
    :param pieData:
    :return:
    """
    data = pieData.items()
    data.sort(key=lambda x:x[1],reverse=True)
    s = float(sum([item[1] for item in data]))
    suggestion = [item for item in data if item[1] > 0]
    tips=[]

    fst = {'0':u"居多，", '1':u"第二，", '2':"第三，"}
    if s>0:
        count=0
        for item in data:
            if item[1]>0:
                tips.append(u'“%s”相关页面访问量%s占%s%%'%(item[0],fst.get(str(count),""),(round(item[1]/s,3))*100))
            count +=1
        s_length = len(suggestion)
        if s_length == 1:
            tips.append(u'【这一段时间内仅访问了“%s”，需要注意平衡一下上网规划哦！】'%suggestion[0][1])
        elif suggestion[0][1] / float(suggestion[1][1]) > 2.0:
            tips.append(u'【“%s”相关界面访问量远多于“%s”，对于重点关注事项要尽可能做好总结哦。】'%(suggestion[0][0],suggestion[1][0]))
        if suggestion[0][1] / float(suggestion[-1][1]) > 30.0:
            tips.append(u'【意外的访问了些许“%s”相关页面，可能需要检查一下是否疏漏什么细节？】'%suggestion[-1][0])
        # if firstItem > 0:
        #     tips.append(u'"%s"相关页面访问量居多，占%s%%'%(firstItem[0],(round(firstItem[1]/s,3))*100))
        # if secondItem > 0:
        #     tips.append(u'"%s"相关页面访问量第二，占%s%%'%(secondItem[0],(round(secondItem[1]/s,3))*100))
        # if thirdItem > 0:
        #     tips.append(u'"%s"相关页面访问量第三，占%s%%'%(thirdItem[0],(round(thirdItem[1]/s,3))*100))
    return tips
def count(seq, pred):
    return sum(1 for v in seq if pred(v))
