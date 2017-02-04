# coding=utf-8
from django import forms
from django.core.exceptions import ValidationError

from dashboard.models import User, LocalAuth
from dashboard.util import DashBoardBackend


class UserLoginForm(forms.Form):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    user_name = forms.CharField(error_messages={'required': u'用户名不能为空'})
    password = forms.CharField(error_messages={'required': u'密码不能为空'})

    class Meta:
        fields = ("user_name", 'password')

    # def clean_username(self):
    #     # Check that the two password entries match
    #     user_name = self.data.get("username")
    #     return check_username(user_name,reverse=True)



def check_username(username,reverse=False):
    if len(username)<=255:
        try:
            u=User.objects.get(user_name=username)
            if  reverse:
                return username
            else:
                raise ValidationError(u'用户已存在',)
        except User.DoesNotExist:
            if reverse:
                raise ValidationError(u'用户不存在',)
            else:
                return username
    else:
        raise ValidationError(u'用户名长度太长',)


class UserRegisterForm(forms.Form):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    user_name = forms.CharField(required=True, error_messages={'required': u'用户名不能为空'})
    nickname = forms.CharField(max_length=255)
    password = forms.CharField(error_messages={'required': u'密码不能为空'})
    password2 = forms.CharField(error_messages={'required': u'验证密码不能为空'})

    class Meta:
        fields = ("user_name", 'nickname', 'password', 'password2')

    # def clean_username(self):
    #     # Check that the two password entries match
    #     user_name = self.data.get("username")
    #     return check_username(user_name)
    #
    # def clean_nickname(self):
    #         # Check that the two password entries match
    #         nickname = self.data.get("nickname")
    #         if len(nickname)<=255:
    #             return nickname
    # def clean_password(self):
    #     if not self.data.get("password"):
    #         raise ValidationError(u'密码不能为空')

    def clean_password2(self):
        # Check that the two password entries match
        password = self.data.get("password")
        password2 = self.data.get("password2")
        if not password2:
            raise ValidationError(u'验证密码不能为空')
        if password and password==password2:
            return password2
        else:
            raise ValidationError(u'验证密码不同')
            # raise ValidationError(
            #     _('Invalid value: %(value)s'),
            #     code='invalid',
            #     params={'value': '42'},
            # )


    def save(self, commit=True):
        if self.is_valid():
            user_name = self.data.get('user_name')
            nickname = self.data.get('nickname')
            password = self.data.get('password')
            u=User(user_name=user_name,
                   nickname=nickname)
            u.save()

            l=LocalAuth(user_id=u.id,password=password)
            l.save()
        else:
            raise ValidationError(self.errors)
