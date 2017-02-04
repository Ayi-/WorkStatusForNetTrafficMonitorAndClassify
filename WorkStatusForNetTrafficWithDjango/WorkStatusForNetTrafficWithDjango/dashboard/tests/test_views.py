#!/usr/bin/env python
# coding=utf-8

import datetime
from django.utils import timezone
from django.test import TestCase

class LoginTestCase(TestCase):
    def setUp(self):
        pass

    def test_login_view(self):
        response = self.client.get('/dashboard/login')
        self.assertEqual(response.status_code,200)

    def test_login_require(self):
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code,302)
        self.assertNotEqual(response.url.find('next'),-1)