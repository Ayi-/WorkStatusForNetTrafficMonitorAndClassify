from django.contrib import admin
from models import User,LocalAuth,UrlData,UrlDataAdmin,TitleClassificationLib,WordVocabulary,TitleClassificationLibAdmin,CategoryTitle
# Register your models here.
admin.site.register(User)
admin.site.register(LocalAuth)
admin.site.register(TitleClassificationLib,TitleClassificationLibAdmin)
admin.site.register(WordVocabulary)
admin.site.register(CategoryTitle)
admin.site.register(UrlData,UrlDataAdmin)