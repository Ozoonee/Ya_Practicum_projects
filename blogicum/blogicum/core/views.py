from django.contrib.auth.views import LogoutView
from django.shortcuts import render


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


def server_error(request, exception=None):
    return render(request, 'pages/500.html', status=500)


class CustomLogoutView(LogoutView):
    http_method_names = ["get", "post", "options"]

    def get(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
