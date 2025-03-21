from django.urls import path
from .views import TestView, QuestionView, AnswerView

urlpatterns = [
    path('tests/', TestView.as_view(), name='test-list-create'),  # Get all tests & create new test
    path('tests/<int:pk>/', TestView.as_view(), name='test-update'),  # Update specific test

    path('questions/', QuestionView.as_view(), name='question-list-create'),  # Get all questions & create new question
    path('questions/<int:pk>/', QuestionView.as_view(), name='question-update'),  # Update specific question

    path('answers/', AnswerView.as_view(), name='answer-list-create'),  # Get all answers & create new answer
    path('answers/<int:pk>/', AnswerView.as_view(), name='answer-update'),  # Update specific answer
]
