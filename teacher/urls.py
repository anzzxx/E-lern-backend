from django.urls import path
from .views import *

urlpatterns = [
    path('create-instructor/', CreateInstructorView.as_view(), name='create-instructor'),
    path('list-instructors/', RetriveInstructorView.as_view(), name='list-instructor'),
    path('profile/retrieve/<int:instructorId>/', RetrieveInstructorProfile.as_view(), name='retrieve-instructor-profile'),
    path('user/<int:user_id>/', InstructorDetailByUserView.as_view(), name='instructor-by-user'),
    path('totel-revenue/', InstructorPayoutStatsView.as_view(), name='instructor-revenue'),

    path('average-rating/',InstructorAvgCourseRatingView.as_view(),name='instructor-avg-rating'),
    path('students/list',InstructorStudentListView.as_view(),name='instructor-paid-students'),

    path('sales-data/', InstructorSalesDataView.as_view(), name='instructor-sales-data'),
    path('course-sales/', InstructorCourseSalesView.as_view(), name='instructor-course-sales'),


]

