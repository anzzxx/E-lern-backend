from django.urls import path
from .views import *

urlpatterns = [
    path('users/', UserListView.as_view(), name='user_list'),  # GET all users
    path('users/<int:id>/', UserUpdateView.as_view(), name='update_user'),  # PATCH update user is_active
    path("superuser-login/",SuperuserLoginView.as_view(), name="superuser-login"),
    path("inactive-courses/", InactiveCourseListView.as_view(), name="inactive-courses-api"),
    path("activate-course/<int:pk>/", ActivateCourseView.as_view(), name="activate-course-api"),
]
