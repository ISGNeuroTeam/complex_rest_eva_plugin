from django.urls import re_path
from eva_plugin.quizs.views import *


urlpatterns = [
    re_path(r'^quizs/?$', QuizsHandler.as_view()),
    re_path(r'^quiz/?$', QuizHandler.as_view()),
    re_path(r'^quiz/create/?$', QuizHandler.as_view()),
    re_path(r'^quiz/edit/?$', QuizHandler.as_view()),
    re_path(r'^quiz/delete/?$', QuizHandler.as_view()),
    re_path(r'^quiz/filled/?$', QuizFilledHandler.as_view()),
    re_path(r'^quiz/filled/save/?$', QuizFilledHandler.as_view()),
    re_path(r'^quiz/filled/export/?$', FilledQuizExportHandler.as_view()),
    re_path(r'^quiz/questions/?$', QuizQuestionsHandler.as_view()),
    re_path(r'^quiz/export/?$', QuizExportJsonHandler.as_view()),
    re_path(r'^quiz/import/?$', QuizImportJsonHandler.as_view()),
]
