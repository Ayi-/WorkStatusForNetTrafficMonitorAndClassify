# coding=utf-8
from django.conf import settings
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, render_to_response, redirect

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from dashboard.forms import UserLoginForm, UserRegisterForm
from dashboard.util import DashBoardBackend, login, login_required, logout
import jwt
import datetime


def loginView(request):
    """
    后台登录
    """
    requestMethod = request.method
    if requestMethod == 'GET':
        if request.user.is_authenticated():
            return HttpResponse('hello Z')
        return render(request,'login/login.html')
    elif requestMethod == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username=form.data.get('user_name')
            password=form.data.get('password')
            user=DashBoardBackend().authenticate(username=username,password=password)
            if user :
                login(request,user)
                return redirect('dashboard')

        return render(request,'login/login.html')
    # return HttpResponse('hello world')

def RegisterView(request):
    """
    后台登录
    """
    requestMethod = request.method
    if requestMethod == 'POST':
        form = UserRegisterForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboardlogin')
        return render(request,'login/login.html')

@login_required
def indexView(request):
    """
    首页
    :param request:
    :return:
    """

    return render(request, 'index.html')


@login_required
def testView(request):
    """
    测试页
    :param request:
    :return:
    """

    return render(request, 'index_line.html')


@login_required
def logoutView(request):
    logout(request)
    return redirect(loginView)

@require_http_methods(["POST",])
@csrf_exempt
def obtainToken(request):
    """
    获取token
    :url:http://www.example.com/dashboard/api/obtain-token/
        :method:post
        :data:{'username':'username','password':'password'}
    :param request:
    :return:
    """
    data = request.POST
    result = {'status':'error','result':u'数据格式错误'}
    form = UserLoginForm(data=data)
    if form.is_valid():
        user_name = form.data.get('user_name')
        password = form.data.get('password')
        user = DashBoardBackend().authenticate(username=user_name, password=password)
        if user:
            exp = datetime.datetime.combine(datetime.datetime.utcnow().date(), datetime.time.min)\
                  + datetime.timedelta(days=3)
            payload = {
                'user_name':user.user_name,
                'user_id':user.id,
                'exp':exp
            }
            token = jwt.encode(payload=payload,key=settings.SECRET_KEY)
            result['status'] = 'ok'
            result['result'] = token
        else:
            result['result'] = u'用户名或密码错误'
    else:
        result['result'] = form.errors
    return JsonResponse(result)

@require_http_methods(["GET",])
@csrf_exempt
def verifyToken(request):
    """
    校验token
    :url:http://www.example.com/dashboard/api/verify-token/
    :method:get
    :data:
    :param request:
    :return:
    """
    token = request.META.get('HTTP_AUTHORIZATION','')
    result = {'status':'error','result':u'数据格式错误'}
    if token:
        try:
            jwt.decode(token,key=settings.SECRET_KEY)
            result['status'] = 'ok'
            result['result'] = token
        except jwt.ExpiredSignatureError:
            result['result'] = u'Token已过期'
        except jwt.DecodeError:
            result['result']=u'非法Token'
        except Exception as e:
            result['result'] = e.message
#eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyNCwidXNlcl9uYW1lIjoidGVzdCIsImV4cCI6MTQ3NjQwMzIwMH0.vdYoWeMoOiGKwnFX9b2bPZe_3QSzJkURsFk_ueg8mgg
    return JsonResponse(result)


import os, sys
lib_path = os.path.abspath(os.path.join('..', 'task'))
sys.path.append(lib_path)
from celerys import naiveBayesMultinomialNB
from django.contrib import messages



@require_http_methods(["GET",])
@login_required
def startNaiveBayesMultinomialNBTask(request):
    """
    启动分类任务，进行分类操作
    :param request:
    :return:
    """

    naiveBayesMultinomialNB.apply_async()
    messages.add_message(request=request,message=u"启用任务成功",level=messages.SUCCESS)
    return redirect(request.META.get('HTTP_REFERER'))