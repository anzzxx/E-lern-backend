from django.urls import path
from .views import *

urlpatterns = [
    # path('courses/', CourseListCreateView.as_view(), name='course-list-create'),  # GET (list) & POST (create)
    # path('courses/<int:pk>/', CourseRetrieveUpdateDestroyView.as_view(), name='course-detail'),  # GET, PUT, DELETE
    path('<int:courseId>/<int:reportId>/',ReportCourseDetailsView.as_view(), name='course-detail'),
    path("courses/", CourseListView.as_view(), name="course-list"),
    path("list/",  CourseAllListView.as_view(), name="course-list"),
    path("create/", CourseCreateView.as_view(), name="course-list"),
    path("courses/<int:pk>/", CourseDetailView.as_view(), name="course-detail"),
    path('enrollments/', UserEnrolledCoursesView.as_view(), name='enrollment-list'),
    path('report-course/', CourseReportCreateView.as_view(), name='report-course'),
    path('reports/', CourseReportListView.as_view(), name='reports-list'),  
    
    path('students-progress/', StudentsProgressListView.as_view(), name='student-progress'),  

]
