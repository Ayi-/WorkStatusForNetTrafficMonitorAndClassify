# coding=utf-8
import logging

import time

import math
from django.db import transaction
from rest_framework import serializers
from django.db import connection,transaction
import re
from rest_framework import permissions



from dashboard.models import User, UrlData



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'id', 'user_name',)



class UrlDataListSerializer(serializers.ListSerializer):


    query = '''INSERT INTO dashboard_urldata
            (`url`,`host`,`scheme`,`content_length`,`timestamp`,`title`,`status`,`category`,`record`,`accuracy`)
            VALUES (%(url)s,%(host)s,%(scheme)s,%(content_length)s,%(timestamp)s,%(title)s,0,NULL,0,0)'''
    def to_internal_value(self, data):
        """
        List of dicts of native values <- List of dicts of primitive datatypes.
        """

        ret = []
        errors = []

        for item in data:
            try:
                validated = self.child.run_validation(item)
            except serializers.ValidationError as exc:
                errors.append(exc.detail)
            else:
                ret.append(validated)

        if any(errors):
            raise serializers.ValidationError(errors)

        return ret

    @transaction.atomic()
    def create(self, validated_data):
        cursor = connection.cursor()
        try:
            with transaction.atomic():
                result = cursor.executemany(self.query,validated_data)
                # raise transaction.DatabaseError
        except Exception as e:
            result = e.message
            if not result:
                result = ','.join([str(i) for i in e.args])
            logging.critical("%s function res:%s e:%s"%("UrlDataListSerializer create",result,e), )
        finally:
            cursor.close()
        return result

# data=[{'url':'http://www.baidu.com','host':'www.baidu.com','scheme':'http','content_length':0,"timestamp":'2001'},{'url':'http://www.zhihu.com','host':'www.zhihu.com','scheme':'http','content_length':0,"timestamp":'2002'}]

class UrlDataSerializer(serializers.ModelSerializer):
    # url = serializers.CharField(max_length=2083,error_messages={'required':u'url为必填项','blank':u'url不能为空'})
    # host = serializers.CharField(max_length=68,error_messages={'required':u'host为必填项','blank':u'host不能为空'})
    # scheme = serializers.CharField(max_length=10,default="http")
    # content_length = serializers.IntegerField(default=0)
    # timestamp = serializers.IntegerField(default=0,)
    # title = serializers.CharField(max_length=2047,allow_blank=True,default="")

    # r'^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)+([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*(:[0-9]+)?[A-Za-z0-9])$',
    # 支持普通url以及IP+host的URL
    patternHost = re.compile(
        r'^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)+([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*(:[0-9]+)?[A-Za-z0-9])$',
        re.I)
    #learn form https://segmentfault.com/q/1010000000135951
    #((https?|s?ftp|irc[6s]?|git|afp|telnet|smb):\/\/)?([a-z0-9]([\w]*[a-z0-9])*\.)?[a-z0-9]\w*\.[a-z]{2,}(\.[a-z]{2,})?(\/\S*)?

    #learn form https://segmentfault.com/q/1010000000584340
    # \b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))


    # '((https?|s?ftp|irc[6s]?|git|afp|telnet|smb):\/\/)?(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)+([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-])+(:[0-9]+)?(\/\S*)?'
    # 支持普通url以及IP+host的URL
    patternUrl = re.compile(
        '((https?|s?ftp|irc[6s]?|git|afp|telnet|smb):\/\/)?(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)+([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-])+(:[0-9]+)?(\/\S*)?')
    class Meta:
        list_serializer_class = UrlDataListSerializer
        model = UrlData
        fields = '__all__'

        # fields = '__all__'

# http://202.38.128.93:96/JZSearch/
# http://jiebademo.ap01.aws.af.cm/s.测试..///df/
    def create(self, validated_data):

        return UrlData.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.url = validated_data.get('url', instance.url)
        instance.host = validated_data.get('host', instance.host)
        instance.scheme = validated_data.get('scheme', instance.scheme)
        instance.content_length = validated_data.get('content_length', instance.content_length)
        instance.timestamp = validated_data.get('timestamp', instance.timestamp)
        instance.title = validated_data.get('title','')
        instance.save()
        return instance

    def validate(self, data):
        """
        Check that the start is before the stop.
        """
        error=[]
        url = data.get('url')
        host = data.get('host')
        timestamp = data.get('timestamp')

        if not self.patternHost.match(host):
            error.append(u"不是合法的host")
        result = self.patternUrl.match(url)
        if not result or len(result.string)!=len(result.group()):
            error.append(u"不是合法的url")
        if timestamp == 0:
            error.append(u"timestamp不能为0")

        if any(error):
            raise serializers.ValidationError({timestamp:error})
        return data



