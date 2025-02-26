from django.urls import path
from .views import *

urlpatterns = [
    # path('courses/', CourseListCreateView.as_view(), name='course-list-create'),  # GET (list) & POST (create)
    # path('courses/<int:pk>/', CourseRetrieveUpdateDestroyView.as_view(), name='course-detail'),  # GET, PUT, DELETE
    path("courses/", CourseListCreateView.as_view(), name="course-list"),
    path("courses/<int:pk>/", CourseDetailView.as_view(), name="course-detail"),
]
