from django.urls import path
from .views import *

urlpatterns = [
    path('get-lessons/', LessonListCreateView.as_view(), name='lesson-list-create'),
    path('edit-lessons/<int:pk>/', LessonRetrieveUpdateDestroyView.as_view(), name='lesson-detail'),
]
