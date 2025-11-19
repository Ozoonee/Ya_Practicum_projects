from django.urls import include, path
from .views import CustomLogoutView

urlpatterns = [
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('', include('django.contrib.auth.urls')),
]
