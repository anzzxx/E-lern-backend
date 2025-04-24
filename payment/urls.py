from django.urls import path
from .views import *

urlpatterns = [
    path("create-payment/", CreatePaymentView.as_view(), name="create_order"),
    path("verify-payment/", VerifyPaymentView.as_view(), name="verify-payment"),
    path('payment-details/', PaymentListView.as_view(), name='payment-list'),
    path('enrollments/<int:instructor_id>/', InstructorEnrollmentStats.as_view(), name='instructor-enrollments'),
    path('<int:instructor_id>/monthly-stats/', InstructorMonthlyStatsView.as_view(), name='instructor-monthly-stats'),
    path('payout-summary/<int:instructor_id>/', InstructorPayoutSummary.as_view(), name='instructor-payout-summary'),
    path('payout/create/', InstructorPayoutCreateView.as_view(), name='instructor-payout-create'),
    path('payout-status/<int:instructor_id>/<str:date>/', InstructorPayoutStatusView.as_view(), name='instructor-payout-status'),


]