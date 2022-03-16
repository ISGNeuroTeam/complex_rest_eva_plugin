from django.urls import re_path
from .views.hello import HelloView
from .views.quizs import (QuizsHandlerView, QuizHandlerView, QuizFilledHandlerView, QuizQuestionsHandlerView,
                          QuizExportJsonHandlerView, QuizImportJsonHandlerView, CatalogsListHandlerView,
                          CatalogHandlerView, FilledQuizExportHandlerView)

urlpatterns = [
    re_path('hello/', HelloView.as_view()),
    re_path(r'^qapi/quizs/?$', QuizsHandlerView.as_view()),
    re_path(r'^qapi/quiz/?$', QuizHandlerView.as_view()),
    re_path(r'^qapi/quiz/create/?$', QuizHandlerView.as_view()),
    re_path(r'^qapi/quiz/edit/?$', QuizHandlerView.as_view()),
    re_path(r'^qapi/quiz/delete/?$', QuizHandlerView.as_view()),
    re_path(r'^qapi/quiz/filled/?$', QuizFilledHandlerView.as_view()),
    re_path(r'^qapi/quiz/filled/save/?$', QuizFilledHandlerView.as_view()),
    re_path(r'^qapi/quiz/questions/?$', QuizQuestionsHandlerView.as_view()),
    re_path(r'^qapi/quiz/export/?$', QuizExportJsonHandlerView.as_view()),
    re_path(r'^qapi/quiz/import/?$', QuizImportJsonHandlerView.as_view()),
    re_path(r'^qapi/catalogs/?$', CatalogsListHandlerView.as_view()),
    re_path(r'^qapi/catalog/?$', CatalogHandlerView.as_view()),
    re_path(r'^qapi/catalog/create/?$', CatalogHandlerView.as_view()),
    re_path(r'^qapi/catalog/edit/?$', CatalogHandlerView.as_view()),
    re_path(r'^qapi/catalog/delete/?$', CatalogHandlerView.as_view()),
    re_path(r'^qapi/quiz/filled/export/?$', FilledQuizExportHandlerView.as_view()),
]