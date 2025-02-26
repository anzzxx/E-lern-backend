from django.urls import path
from .views import *

urlpatterns = [
    path('create-instructor/', CreateInstructorView.as_view(), name='create-instructor'),
]
