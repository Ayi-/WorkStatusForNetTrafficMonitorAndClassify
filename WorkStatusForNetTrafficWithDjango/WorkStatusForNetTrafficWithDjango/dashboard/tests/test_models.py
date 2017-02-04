#!/usr/bin/env python
# coding=utf-8

import datetime

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db import transaction
from django.utils import timezone
from django.test import TestCase
import logging
from django.utils.translation import ugettext_lazy as _

from dashboard.forms import UserLoginForm, UserRegisterForm
from dashboard.models import User, LocalAuth


class UserTestCase(TestCase):
    def setUp(self):
        pass

    def test_create(self):
        # 添加新用户,使用create函数
        user_create = User.objects.create(user_name="eli", nickname="aiiyi")
        self.assertEqual(user_create != None, True)
        # 添加新用户，使用save
        user_save = User(user_name="eli2", nickname="aiiyii")
        user_save.save()
        self.assertEqual(user_save != None, True)

        # 添加用户，用户名已存在
        # create
        with self.assertRaises(ValidationError) as cm, transaction.atomic():
            User.objects.create(user_name="eli", nickname="aiiyi")
        self.assertEqual(cm.exception.args[0].get('user_name')[0].message, _(u"用户名已存在"))

        # save
        user_save = User(user_name="eli2", nickname="aiiyii")
        with self.assertRaises(ValidationError) as cm:
            transaction.atomic()
            user_save.save()
        self.assertEqual(cm.exception.args[0].get('user_name')[0].message, _(u"用户名已存在"))

        # 添加用户，用户名为空
        # save
        user_save = User()
        with self.assertRaises(ValidationError) as cm:
            transaction.atomic()
            user_save.save()

        self.assertEqual(cm.exception.error_dict.get('__all__')[0].message, _(u"用户名不能为空"))


class LocalAuthTestCase(TestCase):
    def setUp(self):
        User.objects.create(pk='33', user_name="eli", nickname="aiiyi")
        User.objects.create(pk='34', user_name="eli2", nickname="aiiyi2")

    def test_create(self):
        # 添加用户密码
        user_auth_create = LocalAuth.objects.create(user_id='33', password="test")
        self.assertEqual(user_auth_create != None, True)
        # 添加用户密码，使用save
        user_auth_save = LocalAuth(user_id='34', password="test")
        user_auth_save.save()
        self.assertEqual(user_auth_save != None, True)

        # 测试密码验证
        user = LocalAuth.objects.get(user_id='33')
        self.assertEqual(user.check_password('test'), True)
        self.assertEqual(user.check_password('test1'), False)

        # 添加用户密码，用户密码已设置
        # create
        with self.assertRaises(ValidationError) as cm:
            transaction.atomic()
            LocalAuth.objects.create(user_id='33', password="test")


        self.assertEqual(cm.exception.args[0].get('__all__')[0].message, _(u"该用户已设置密码"))

        with self.assertRaises(ValidationError) as cm:
            transaction.atomic()
            l=LocalAuth.objects.create()
            logging.critical(l.__dict__)
            logging.critical(l.password)
        self.assertEqual(cm.exception.error_dict.get('__all__')[0].message, _(u"用户ID不能为空"))
        self.assertEqual(cm.exception.error_dict.get('__all__')[1].message, _(u"用户ID不存在"))
        self.assertEqual(cm.exception.error_dict.get('__all__')[2].message, _(u"密码不能为空"))
