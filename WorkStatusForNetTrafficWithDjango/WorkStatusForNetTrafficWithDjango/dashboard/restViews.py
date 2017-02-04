# coding=utf-8
import json
import math

import itertools

import datetime
from django.db import transaction
from django.http import JsonResponse
from rest_framework import generics
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.exceptions import MethodNotAllowed, ValidationError
from rest_framework.response import Response

from dashboard.models import User, UrlData, CategoryTitle
from dashboard.permissions import IsLoginReadOnly
from dashboard.serializers import UserSerializer, UrlDataSerializer
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from dashboard.util import JWTAuthentication, keyForGroupByDatetimeHour, getShangHaiDateTimeFromTimestamp, \
    countGroupByCategoryWithTimeGroup,countGroupByCategoryWithFullGroup,getTipsForPieData


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UrlDataViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    serializer_class = UrlDataSerializer
    permission_classes = (IsLoginReadOnly,)
    authentication_classes = (JWTAuthentication, SessionAuthentication)

    def get_queryset(self):
        minTimestamp = self.request.query_params.get('minTimestamp', False)
        maxTimestamp = self.request.query_params.get('maxTimestamp', False)
        if minTimestamp and maxTimestamp:
            return UrlData.objects.filter(timestamp__range=[minTimestamp, maxTimestamp])
        else:
            return UrlData.objects.all()

    def http_method_not_allowed(self, request, *args, **kwargs):
        """
        If `request.method` does not correspond to a handler method,
        determine what kind of exception to raise.
        """
        raise MethodNotAllowed(None, detail=u'不支持“{method}"请求方法'.format(method=request.method))

    def destroy(self, request, *args, **kwargs):
        content = {'status': 'error', 'result': u'不支持的请求方式'}
        return Response(content, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @list_route(methods=['post'])
    def bulkCreate(self, request):
        """
        :url:http://www.example.com/dashboard/api/url_data/bulkCreate
        :method:post
        :data:urlData=[{"url":"http://www.example.com/example",
            "host":"www.example.com",
            "scheme":"http",
            "content_length":1024,
            "timestamp":"1990",
            "title":"example"},]
        :param request: request
        :return: {'status':'ok','result':'result'}
        """
        try:
            data = json.loads(request.data.get('urlData', ''))
        except Exception as e:
            data = ''
        result = {'status': 'error'}
        resultStatus = status.HTTP_400_BAD_REQUEST
        length = len(data)
        if length < 1:
            result[
                'result'] = u"""上传数据的格式错误：{"urlData":[{"url":"http://www.example.com",""" \
                            u""""host":"www.example.com","scheme":"http","content_length":1024,"timestamp":"2001"}]}"""
        elif length > 10000:
            result['result'] = u'数据量不可超过10000条'
        else:
            # return Response(serializer.data)

            errors = []

            res = ''
            ins = self.get_serializer(data=data, many=True)
            if ins.is_valid():
                res = ins.create(ins.validated_data)
            else:
                errors.append(ins.errors)

            if isinstance(res, (int, long)):
                result = {'status': 'ok', 'result': res}

                resultStatus = status.HTTP_200_OK

            else:
                resultStatus = status.HTTP_400_BAD_REQUEST
                0 if len(res) < 1 else errors.append(res)
                result['result'] = errors

        return JsonResponse(result, status=resultStatus)


class TitleCategoryList(viewsets.mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """
    根据timestamp区间范围获取分类情况
    """
    http_method_names = ['get']  # 需要小写
    permission_classes = (IsLoginReadOnly,)
    authentication_classes = (JWTAuthentication, SessionAuthentication)

    def get_queryset(self):
        """
        根据时间戳返回记录
        :return:
        """
        try:
            minTimestamp = int(self.request.query_params.get('minTimestamp', ''))
            maxTimestamp = int(self.request.query_params.get('maxTimestamp', ''))

            if minTimestamp and maxTimestamp:
                return UrlData.objects.filter(timestamp__range=[minTimestamp, maxTimestamp], category__isnull=False).order_by('timestamp')
        except:
            pass

        error = u"minTimestamp或者maxTimestamp错误"
        raise ValidationError(detail=error)

    def list(self, request, *args, **kwargs):
        """
        返回横轴+数据
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        queryset = self.get_queryset()

        # data = UrlData.objects.filter(timestamp__range=[minTimestamp, maxTimestamp])
        statusCode = status.HTTP_200_OK
        type = self.request.query_params.get('type', False)
        result = {'status': ['ok']}

        # 返回点的数据
        if type == 'scatter':
            # data = [list(group) for k, group in itertools.groupby(queryset, key=keyForGroupByDatetimeHour)]
            # timeGroup = [
            #     [[getShangHaiDateTimeFromTimestamp(item.timestamp).strftime("%Y/%m/%d %H:%M:%S"), item.category] for
            #      item in list(group)] for k, group in
            #     itertools.groupby(queryset, key=keyForGroupByDatetimeHour)]
            data = [[[getShangHaiDateTimeFromTimestamp(item.timestamp).strftime("%Y/%m/%d %H:%M:%S"), item.category] for
                     item in list(group)] for k, group in
                    itertools.groupby(queryset, key=lambda x: x.category)]
            result['data'] = data

        elif type == 'line':
            # 返回折线图的数据
            categoryGroup = [list(group) for k, group in itertools.groupby(queryset, key=keyForGroupByDatetimeHour)]
            result['data'] = countGroupByCategoryWithTimeGroup(categoryGroup)
        elif type == 'query':
            key = self.request.query_params.get('category', False)
            if key:
                data = [[ item.title, getShangHaiDateTimeFromTimestamp(item.timestamp).strftime("%Y/%m/%d %H:%M:%S"), item.url] for item
                        in queryset.filter(category=key)]
                result['data'] = data
        elif type=='pie':
            data=countGroupByCategoryWithFullGroup(queryset)
            result['data'] = data
            tips = getTipsForPieData(data)
            if any(tips):
                result['tips'] = tips
                # tags = [getShangHaiDateTimeFromTimestamp(item[0].timestamp).strftime("%Y/%m/%d %H") for item in data]
        else:
            result['status'] = ['error']
        if result['status'][0]=='ok':
            result['categoryList']=[item[0] for item in CategoryTitle.objects.values_list('word')]
        return JsonResponse(data=result, status=statusCode)
