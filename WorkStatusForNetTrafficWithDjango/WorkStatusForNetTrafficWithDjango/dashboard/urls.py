
from django.conf.urls import url, include
from . import views
from rest_framework import routers

from . import restViews
from rest_framework.routers import Route, DynamicDetailRoute, SimpleRouter, SimpleRouter, DynamicListRoute


class CustomRouter(SimpleRouter):
    """
    A router for read-only APIs, which doesn't use trailing slashes.
    """
    # List route.
    routes = [
        # List route.
        Route(
            url=r'^{prefix}/$',
            mapping={
                'get': 'list',
                'post': 'create'
            },
            name='{basename}-list',
            initkwargs={'suffix': 'List'}
        ),
        # Dynamically generated list routes.
        # Generated using @list_route decorator
        # on methods of the viewset.
        DynamicListRoute(
            url=r'^{prefix}/{methodname}/?$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
        # Detail route.
        Route(
            url=r'^{prefix}/{lookup}/?$',
            mapping={
                'get': 'retrieve',
                'put': 'update',
                'patch': 'partial_update',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            initkwargs={'suffix': 'Instance'}
        ),
        # Dynamically generated detail routes.
        # Generated using @detail_route decorator on methods of the viewset.
        DynamicDetailRoute(
            url=r'^{prefix}/{lookup}/{methodname}/?$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
    ]

router = CustomRouter(trailing_slash=False)
# router = SimpleRouter(trailing_slash=False)
router.register(r'users', restViews.UserViewSet,'user')
router.register(r'url_data', restViews.UrlDataViewSet,base_name='url_data')
router.register(r'titlecategorylist', restViews.TitleCategoryList,base_name='TitleCategoryList')

urlpatterns = [
    url(r'^/api/', include(router.urls)),
    url(r'^/login/?$', views.loginView,name='dashboardlogin'),
    url(r'^/logout/?$', views.logoutView),
    url(r'^/register/?$', views.RegisterView,name='dashboard_register'),
    url(r'^/index/?$', views.indexView,name='dashboard'),
    url(r'^/?$', views.indexView),
    url(r'^/test/?$', views.testView),
    url(r'^/api/obtain-token/?$', views.obtainToken),
    url(r'^/api/verify-token/?$', views.verifyToken),
    url(r'^/api/startnaivebayesmultinomialnbtask/?$', views.startNaiveBayesMultinomialNBTask,name='startNaiveBayesMultinomialNBTask'),

]

