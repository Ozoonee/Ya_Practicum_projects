from rest_framework import mixins, status, viewsets
from rest_framework.response import Response


class UpdateDeleteViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    pass


class UserRelationMixin:
    """Mixin for handler favorite, shopping cart, subscribe"""
    def handle_relation_action(self, request, obj, model_class,
                               user_field='user', object_field='recipe',
                               success_message='Успешно добавлено',
                               error_message='Уже существует',
                               not_found_message='Объект не найден'):
        user = request.user
        if request.method == 'POST':
            lookup_params = {
                user_field: user,
                object_field: obj}
            item, created = model_class.objects.get_or_create(**lookup_params)
            if created:
                return Response(
                    {'status': success_message},
                    status=status.HTTP_201_CREATED)
            return Response(
                {'error': error_message},
                status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            filter_params = {
                user_field: user,
                object_field: obj}
            deleted, _ = model_class.objects.filter(**filter_params).delete()
            if deleted:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'error': not_found_message},
                status=status.HTTP_404_NOT_FOUND)
