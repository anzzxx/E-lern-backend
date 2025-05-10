from django.urls import path
from .views import (
    UserListView,
    UserUpdateView,
    SuperuserLoginView,
    InactiveCourseListView,
    ActivateCourseView,
    TotalEnrolledStudentsAPIView,
    TotalRevenueAPIView,
    MonthlyRevenueAPIView,
    CourseAnalyticsView,
)

urlpatterns = [
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<int:id>/', UserUpdateView.as_view(), name='update_user'),
    path("superuser-login/", SuperuserLoginView.as_view(), name="superuser-login"),
    path("inactive-courses/", InactiveCourseListView.as_view(), name="inactive-courses-api"),
    path("activate-course/<int:pk>/", ActivateCourseView.as_view(), name="activate-course-api"),
    path("total-enrolled-students/", TotalEnrolledStudentsAPIView.as_view(), name="total-enrolled-students"),
    path("total-revenue/", TotalRevenueAPIView.as_view(), name="total-revenue"),
    path('monthly-revenue/', MonthlyRevenueAPIView.as_view(), name='monthly-revenue'),
    path('course-analytics/', CourseAnalyticsView.as_view(), name='course-analytics'),
]

