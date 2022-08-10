from django.urls import re_path
from eva_plugin.quizs.views import *


urlpatterns = [
    re_path(r'^qapi/quizs/?$', QuizsHandler.as_view()),
    re_path(r'^qapi/quiz/?$', QuizHandler.as_view()),
    re_path(r'^qapi/quiz/create/?$', QuizHandler.as_view()),
    re_path(r'^qapi/quiz/edit/?$', QuizHandler.as_view()),
    re_path(r'^qapi/quiz/delete/?$', QuizHandler.as_view()),
    re_path(r'^qapi/quiz/filled/?$', QuizFilledHandler.as_view()),
    re_path(r'^qapi/quiz/filled/save/?$', QuizFilledHandler.as_view()),
    re_path(r'^qapi/quiz/questions/?$', QuizQuestionsHandler.as_view()),
    re_path(r'^qapi/quiz/export/?$', QuizExportJsonHandler.as_view()),
    re_path(r'^qapi/quiz/import/?$', QuizImportJsonHandler.as_view()),
    re_path(r'^qapi/quiz/filled/export/?$', FilledQuizExportHandler.as_view()),
]
