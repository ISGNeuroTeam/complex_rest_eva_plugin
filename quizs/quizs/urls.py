from rest.urls import path
from cache import cache_page
from .views.example import ExampleView
from .views.hello import HelloView
from .views.quizs import QuizsHandlerView, QuizHandlerView, QuizFilledHandlerView


# Use cache_page decorator for caching view

# urlpatterns = [
#     path('example/', cache_page(60 * 15)(ExampleView.as_view())),
# ]

urlpatterns = [
path('example/', ExampleView.as_view()),
path('hello/', HelloView.as_view()),
path('qapi/quizs/', QuizsHandlerView.as_view()),
path('qapi/quiz/', QuizHandlerView.as_view()),
path('qapi/quiz/create/', QuizHandlerView.as_view()),
path('qapi/quiz/edit/', QuizHandlerView.as_view()),
path('qapi/quiz/delete/', QuizHandlerView.as_view()),
path('qapi/quiz/filled/', QuizFilledHandlerView.as_view()),
]