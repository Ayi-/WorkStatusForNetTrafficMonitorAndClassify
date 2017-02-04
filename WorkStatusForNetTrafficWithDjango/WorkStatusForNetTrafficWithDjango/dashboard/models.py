# coding=utf-8
import bcrypt
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User as adminUser
# Create your models here.
from django.db import transaction
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from dashboard import util


@receiver(pre_save)
def pre_save_handler(sender, instance, *args, **kwargs):
    instance.full_clean()


class User(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    user_name = models.CharField(max_length=255, unique=True, error_messages={'unique': _(u'用户名已存在')})
    nickname = models.CharField(max_length=255)
    register_datetime = models.DateTimeField(auto_now=True)
    lasted_login = models.DateTimeField(null=True)

    is_active = True
    is_admin = False
    backend = 'dashboard.util.DashBoardBackend'

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return False

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return False

    def get_username(self):
        return self.user_name

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    def clean_fields(self, exclude=None):
        self.error = []
        if not self.user_name:
            self.error.append(ValidationError(u"用户名不能为空", code='invalid', ))
        if self.error:
            raise ValidationError(self.error)
            # super(User,self).clean_fields(exclude)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        super(User, self).save(force_insert, force_update, update_fields)

    def is_authenticated(self):
        return True
    def __repr__(self):
        return "%s:%s,%s,%s,%s,%s" % (self.__class__.__name__, self.id,
                                      self.user_name,
                                      self.nickname,
                                      util.getShangHaiDateTimeFromTimestampWithStr(self.register_datetime),
                                      util.getShangHaiDateTimeFromTimestampWithStr(self.lasted_login))

    def __str__(self):
        return self.__repr__()

class LocalAuth(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    # user_id = models.OneToOneField(User,db_column='user_id',on_delete=models.CASCADE,null=False)
    user_id = models.IntegerField(null=False, default=0)
    password = models.CharField(max_length=60, null=False, blank=False)  # 存放hashed

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # self.clean_fields()
        super(LocalAuth, self).save(force_insert, force_update, update_fields)

    def clean_fields(self, exclude=None):
        self.error = []
        if not self.user_id:
            self.error.append(ValidationError(_(u"用户ID不能为空"), code='invalid', ))
        if len(User.objects.filter(pk=self.user_id)) != 1:
            self.error.append(ValidationError(_(u"用户ID不存在"), code='invalid', ))
        if len(LocalAuth.objects.filter(user_id=self.user_id)) >= 1:
            self.error.append(ValidationError(_(u"该用户已设置密码"), code='invalid', ))
        if not self.password:
            self.error.append(ValidationError(_(u"密码不能为空"), code='invalid', ))
        else:
            self.password = bcrypt.hashpw(self.password.encode("utf-8"), bcrypt.gensalt())
        if self.error:
            raise ValidationError(self.error)
            # super(LocalAuth,self).clean_fields(exclude)

    def check_password(self, password):
        return bcrypt.checkpw(password.encode("utf-8"), self.password.encode("utf-8"))

    def __repr__(self):
        return "%s:%s,%s" % (self.__class__.__name__, self.id,self.user_id)

    def __str__(self):
        return self.__repr__()


class CategoryTitle(models.Model):
    """
    分类词
    """
    id = models.AutoField(primary_key=True, auto_created=True)
    # url_id = models.IntegerField()
    word = models.CharField(max_length=50, blank=False, null=False,unique=True)
    def __repr__(self):
        return "%s:%s" % (self.__class__.__name__, self.word)

    def __str__(self):
        return self.__repr__()


import re
class UrlData(models.Model):
    """
    用于存放本地计算机上传上来的url数据
    """
    id = models.AutoField(primary_key=True, auto_created=True)
    url = models.CharField(verbose_name=u'访问地址', max_length=2083, error_messages={'blank': _(u'url不能为空')})
    host = models.CharField(verbose_name=u'访问地址主机', max_length=68, error_messages={'blank': _(u'host不能能为空')})
    scheme = models.CharField(verbose_name=u'协议', max_length=10, default="http")
    content_length = models.IntegerField(verbose_name=u'文本长度', default=0)
    timestamp = models.IntegerField(verbose_name=u'访问时间', default=0.0)
    status = models.IntegerField(verbose_name=u'处理状态', default=0,choices=util.statusList)  # 处理状态
    category = models.CharField(verbose_name=u'分类', max_length=50, blank=True, null=True, default=None,choices=CategoryTitle.objects.values_list('word','word'))  # 分类结果
    record = models.IntegerField(verbose_name=u'是否记录', default=0,choices=util.recordList)  # 是否记录到词库中
    accuracy = models.FloatField(verbose_name=u'准确率', default=0)  # 准确率
    title = models.CharField(verbose_name=u'网址标题', max_length=2047, blank=True, default="")

    patternHost = re.compile(
        r'^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)+([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*(:[0-9]+)?[A-Za-z0-9])$',
        re.I)

    patternUrl = re.compile(
        '((https?|s?ftp|irc[6s]?|git|afp|telnet|smb):\/\/)?(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)+([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-])+(:[0-9]+)?(\/\S*)?')

    def clean_fields(self, exclude=None):
        self.error = []
        if not self.url:
            self.error.append(ValidationError(_(u"url不能为空"), code='invalid', ))
        if not self.host:
            self.error.append(ValidationError(_(u"host不能为空"), code='invalid', ))
        if not self.patternHost.match(self.host):
            self.error.append(ValidationError(u"不是合法的host", code='invalid', ))
        result = self.patternUrl.match(self.url)
        if not result or len(result.string)!=len(result.group()):
            self.error.append(ValidationError(u"不是合法的url", code='invalid', ))
        if self.error:
            raise ValidationError(self.error)

    def __repr__(self):
        return "%s:%s,<%s...>,%s" % (self.__class__.__name__, self.id,self.title[0:15].encode('utf-8'),util.getShangHaiDateTimeFromTimestamp(self.timestamp).strftime('%Y/%m/%d %H:%M:%S'))

    def __str__(self):
        return self.__repr__()

    # class Meta:
    #     verbose_name=u'地址链接数据'
    #     verbose_name_plural=verbose_name





import logging
from django.contrib import messages
class UrlDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'view_title', 'category', 'view_timestamp', 'status', 'record', 'accuracy', 'view_url')
    list_editable=('category','status','record',)
    list_filter = ('category',)
    search_fields = ['title', 'category']
    save_on_top = True

    actions_on_bottom=True
    actions = ['recordToTCL']
    def view_url(self, obj):
        return format_html('<a href="%s">%s</a>' % (obj.url, obj.host))

    view_url.short_description = u'访问地址'
    view_url.admin_order_field = u'url'

    def view_title(self, obj):
        return format_html('<span title="%s">%s</span>' % (obj.title, obj.title))

    view_title.short_description = u'标题'
    view_title.admin_order_field = u'title'

    def view_timestamp(self, obj):
        return util.getShangHaiDateTimeFromTimestamp(obj.timestamp).strftime('%Y/%m/%d %H:%M:%S')

    view_timestamp.short_description = u'访问时间'
    view_timestamp.admin_order_field = u'timestamp'

    def save_model(self, request, obj, form, change):
        if  obj.category in ['',None]:
            obj.status=0
            obj.category=None
            obj.record=0
        else:
            obj.status = 1
        
        obj.save()
        

    @transaction.atomic
    def recordToTCL(self, request, queryset):
        """
        定义一个操作，用于添加指定的记录到分类表（TitleClassificationLib）中
        :param request:
        :param queryset:
        :return:
        """
        success_count = 0
        faile_count = 0
        tmp_messages = []

        for obj in queryset:
            try:

                TitleClassificationLib.objects.create(title=obj.title, category=obj.category)
                obj.record=1
                success_count+=1
            except Exception as e:
                # tmp_messages.append(["%s" % (e), messages.ERROR])
                if hasattr(e,'messages') and hasattr(e,'message_dict') \
                        and (e.messages[-1]!=u'This field cannot be blank.'
                             and e.messages[-1]!=u'This field cannot be null.'
                             and e.messages[-1]!=u'Title classification lib with this Title already exists.'):
                    for k,v in e.message_dict.items():
                        tmp_messages.append(["%s:%s" % (k,v), messages.ERROR])
                else:
                    obj.record = 2
                faile_count += 1
            finally:
                obj.save()
        if success_count:
            tmp_messages.append([u"%s条记录保存成功"%success_count,messages.SUCCESS])
        if faile_count:
            tmp_messages.append([u"%s条记录保存失败，因为表中已经存在对应的记录" % faile_count, messages.WARNING])
        if any(tmp_messages):
            for item in tmp_messages:
                messages.add_message(request=request,level=item[1],message=item[0])
    recordToTCL.short_description = u"添加到分类表中"


    class Media:
        css = {
            "all": ("dashboard/css/url-data.css",)
        }


class TitleClassificationLib(models.Model):
    """
    用于存放title分词后的数据
    category: 娱乐，IT,
    status:0 未处理，1 已处理

    """
    id = models.AutoField(primary_key=True, auto_created=True)
    # url_id = models.IntegerField()
    title = models.CharField(max_length=255,blank=False,null=False,unique=True)
    title_key = models.CharField(max_length=255, blank=True, null=True, default=None)
    category = models.CharField(max_length=50,blank=False,null=False)
    status = models.IntegerField(default=0)

class TitleClassificationLibAdmin(admin.ModelAdmin):
    list_display = ('id','title','category','status')


class WordVocabulary(models.Model):
    """
    存放分词词库
    """
    id = models.AutoField(primary_key=True, auto_created=True)
    # url_id = models.IntegerField()
    word = models.CharField(max_length=50, blank=False, null=False,unique=True)
    # title_key = models.CharField(max_length=2047,blank=True,null=True,default=None)
    freq = models.IntegerField(default=10)
    pos = models.CharField(max_length=50, blank=True, default="")



##############test
# from django.contrib.contenttypes.models import ContentType
# from django.http import HttpResponseRedirect
# def export_selected_objects(modeladmin, request, queryset):
#     selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
#     ct = ContentType.objects.get_for_model(queryset.model)
#     return HttpResponseRedirect("/export/?ct=%s&ids=%s" % (ct.pk, ",".join(selected)))
#
#
# admin.site.add_action(export_selected_objects)