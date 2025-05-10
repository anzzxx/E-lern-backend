from django.urls import path
from .views import *

urlpatterns = [
    path('tests/<int:pk>/', TestView.as_view(), name='test-list'),
    path('test/create/', TestCreateView.as_view(), name='test-create'),
    path('test/<int:pk>/', TestCreateView.as_view(), name='test-update'),
    path('questions/<int:testId>/', QuestionView.as_view(), name='question-list'),
    path('question/create/',QuestionCreateView.as_view(), name='question-create'),
    path('question/<int:pk>/', QuestionCreateView.as_view(), name='question-update'),
    path('answers/<int:questionId>/', AnswerView.as_view(), name='answer-list'),
    path('answer/create/', AnswerCreateView.as_view(), name='answer-create'),
    path('answers/<int:pk>/', AnswerCreateView.as_view(), name='answer-update'),
]