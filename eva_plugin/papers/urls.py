from django.urls import re_path
from eva_plugin.papers.views import PapersHandler, PaperHandler, PaperLoadHandler

urlpatterns = [
    re_path(r'^eva/reports/load/?$', PaperLoadHandler.as_view()),
    re_path(r'^eva/reports/getAll/?$', PapersHandler.as_view()),
    re_path(r'^eva/reports/get/?$', PaperHandler.as_view()),
]

