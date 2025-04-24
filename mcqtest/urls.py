from django.urls import path
from .views import *

urlpatterns = [
    path('tests/<int:pk>/', TestView.as_view(), name='test-list'),
    path('test/create/', TestCreateView.as_view(), name='test-create'),  

    path('questions/<int:testId>/', QuestionView.as_view(), name='question-list'),
    path('question/create/',QustionCreateView.as_view(), name='question-create'),
    path('questions/<int:pk>/', QuestionView.as_view(), name='question-update'), 

    path('answers/<int:qustionId>/', AnswerView.as_view(), name='answer-list'),
    path('answer/create/', AnswerCreateView.as_view(), name='answer-create'),  
    path('answers/<int:pk>/', AnswerView.as_view(), name='answer-update'),
]
