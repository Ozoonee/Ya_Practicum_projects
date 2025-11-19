from django.urls import path
from .views import AboutPage, RulesPage


app_name = 'pages'

handler404 = 'core.views.page_not_found'
handler500 = 'core.views.server_error'

urlpatterns = [
    path('about/', AboutPage.as_view(), name='about'),
    path('rules/', RulesPage.as_view(), name='rules'),
]
