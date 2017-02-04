#!/usr/bin/env python
# coding=utf-8

import datetime

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db import transaction
from django.utils import timezone
from django.test import TestCase
import logging

from dashboard.forms import UserLoginForm,UserRegisterForm
from dashboard.models import User, LocalAuth

class LoginTestCase(TestCase):
    def setUp(self):
        # 添加测试数据
        u=User(user_name='eli_test')
        u.save()
        l=LocalAuth(user_id=u.id,password='test')
        l.save()

    def test_UserRegisterForm(self):
        # 测试 注册表单
        # 完整的测试表单
        post_data = {'user_name':u'elixxx',
                     'nickname':u'eli',
                     'password':u'111',
                     'password2':u'111'}
        form = UserRegisterForm(post_data)

        self.assertEqual(form.is_valid(),True)
        form.save()
        u = User.objects.get(user_name=form.data.get('user_name'))
        self.assertEqual(u.user_name,form.data.get('user_name'))
        l = LocalAuth.objects.get(user_id=u.id)
        self.assertEqual(l.check_password(u'111'),True)

        # 注册已存在的账号
        post_data = {'user_name':u'eli_test',
                     'nickname':u'eli',
                     'password':u'111',
                     'password2':u'111'}

        form = UserRegisterForm(post_data)
            # 验证
        self.assertEqual(form.is_valid(),True)
            # 尝试保存
        with self.assertRaises(ValidationError) as cm, transaction.atomic():
            form.save()

        self.assertEqual(cm.exception.message_dict,{'user_name': [u'用户名已存在']})

        # 用户名为空
        post_data = {'user_name':u'',
                     'nickname':u'eli',
                     'password':u'111',
                     'password2':u'111'}
        form = UserRegisterForm(post_data)
        # 验证
        self.assertEqual(form.is_valid(),False)
        # 尝试保存
        with self.assertRaises(ValidationError) as cm,transaction.atomic():
            form.save()
        self.assertEqual(cm.exception.args[0],{'user_name': [u'用户名不能为空']})

        # 密码为空
        post_data = {'user_name':u'eli_xxxxxx',
                     'nickname':u'eli',
                     'password':u'111',
                     'password2':u''}
        form = UserRegisterForm(post_data)
        # 验证
        self.assertEqual(form.is_valid(),False)
        # 尝试保存
        with self.assertRaises(ValidationError) as cm, transaction.atomic():
            form.save()
        self.assertEqual(cm.exception.args[0],{'password2': [u'验证密码不能为空']})
        # IntegrityError: (1452, 'Cannot add or update a

    def test_UserLoginForm(self):

        post_data = {'user_name':u'eli','password':u'eli'}
        form = UserLoginForm(post_data)
        self.assertEqual(form.is_valid(),True)
        # self.assertEqual(form.errors,{'user_name': [u'用户不存在']})

        post_data = {'user_name':u'eli_test','password':u'test'}
        form = UserLoginForm(post_data)
        self.assertEqual(form.is_valid(),True)

        post_data = {'usernam':u'eli','password':u'eli'}
        form = UserLoginForm(post_data)
        self.assertEqual(form.is_valid(),False)

        post_data = {'usernam':u'eli_test','password':u'test'}
        form = UserLoginForm(post_data)
        self.assertEqual(form.is_valid(),False)

        post_data = {'user_name':u'eli','passwor':u'eli'}
        form = UserLoginForm(post_data)
        self.assertEqual(form.is_valid(),False)

        post_data = {'user_name':u'eli_test','passwor':u'test'}
        form = UserLoginForm(post_data)
        self.assertEqual(form.is_valid(),False)
        self.assertEqual(form.errors,{'password': [u'密码不能为空']})

        post_data = {'user_name':u'','password':u'eli'}
        form = UserLoginForm(post_data)
        self.assertEqual(form.is_valid(),False)
        self.assertEqual(form.errors,{'user_name': [u'用户名不能为空']})

        post_data = {'user_name':u'','password':u'test'}
        form = UserLoginForm(post_data)
        self.assertEqual(form.is_valid(),False)

        post_data = {'user_name':u'eli','password':u''}
        form = UserLoginForm(post_data)
        self.assertEqual(form.is_valid(),False)

        post_data = {'user_name':u'eli_test','password':u''}
        form = UserLoginForm(post_data)
        self.assertEqual(form.is_valid(),False)