from django.urls import re_path
from eva_plugin.indexes.views import *

urlpatterns = [
    re_path(r'^indexes/?$', IndexesHandler.as_view()),
    re_path(r'^index/?$', IndexHandler.as_view()),
    re_path(r'^user/indexes/?$', IndexesHandler.as_view()),
]
