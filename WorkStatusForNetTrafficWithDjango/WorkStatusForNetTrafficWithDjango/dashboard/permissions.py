# -*- coding:utf-8 -*-
from rest_framework import permissions
from django.contrib.auth.models import AnonymousUser

class IsLoginReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_permission(self, request, view):
        return request.user != None and not isinstance(request.user, AnonymousUser)
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.

        # Write permissions are only allowed to the owner of the snippet.

        return request.user!=None and not  isinstance(request.user,AnonymousUser)