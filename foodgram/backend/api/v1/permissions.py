from rest_framework import permissions


class IsAuthenticatedForCreate(permissions.BasePermission):
    '''Create for authenticated users'''
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == 'POST' and hasattr(view, 'action'):
            if view.action in ['shopping_cart', 'favorite']:
                return request.user.is_authenticated
        if request.method == 'POST':
            return request.user.is_authenticated
        return True


class IsAuthorForEdit(permissions.BasePermission):
    '''Read for all, edit for author'''
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if hasattr(view, 'action') and view.action in ['shopping_cart',
                                                       'favorite']:
            return request.user.is_authenticated
        return obj.author == request.user
