from django.urls import re_path, include

from eva_plugin.auth.views import AuthLoginHandler
from eva_plugin.dashs.urls import urlpatterns as dash_urlpatterns
from eva_plugin.groups.urls import urlpatterns as group_urlpatterns

urlpatterns = [
    re_path(r'auth/login/?', AuthLoginHandler.as_view()),
] + dash_urlpatterns + group_urlpatterns
