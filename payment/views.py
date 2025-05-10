from django.conf import settings
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.db.models.functions import TruncMonth
from django.db.models import Count, Sum
from django.utils.timezone import make_aware
from datetime import datetime, timedelta, date
import json
import calendar
import razorpay
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics

from .models import Payment, MonthlyCourseStats, InstructorPayout
from accounts.models import CustomUser as User
from Courses.models import Course, Enrollment, StudentCourseProgress
from teacher.models import Instructor
from .serializers import (
    PaymentSerializer,
    MonthlyCourseStatsSerializer,
    InstructorPayoutSerializer
)

# Initialize Razorpay client
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)


class CreatePaymentView(APIView):
    """
    API endpoint for creating Razorpay payment orders.
    Requires authenticated user and course details.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Create a Razorpay payment order.
        
        Args:
            request: Contains amount and course_id
            
        Returns:
            JsonResponse: Razorpay order details or error message
        """
        try:
            data = request.data
            amount = int(data.get("amount", 0)) * 100  # Convert to paisa
            course_id = data.get("course_id")
            user_id = request.user.id
            
            if not amount or not course_id:
                return JsonResponse(
                    {"success": False, "message": "Missing required fields"},
                    status=400
                )
            
            order_data = {
                "amount": amount,
                "currency": "INR",
                "payment_capture": "1",
            }
            
            order = razorpay_client.order.create(order_data)
            return JsonResponse(order)
        
        except Exception as e:
            return JsonResponse(
                {"success": False, "error": str(e)},
                status=500
            )


class VerifyPaymentView(APIView):
    """
    API endpoint for verifying Razorpay payments and processing enrollments.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Verify payment signature and process course enrollment.
        
        Args:
            request: Contains payment verification details
            
        Returns:
            JsonResponse: Payment verification status
        """
        try:
            data = request.data
            payment_id = data.get("payment_id")
            order_id = data.get("order_id")
            signature = data.get("signature")
            course_id = data.get("course_id")
            
            if not all([payment_id, order_id, signature]):
                return JsonResponse(
                    {"success": False, "message": "Missing payment details"},
                    status=400
                )
            
            params_dict = {
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }
            
            try:
                razorpay_client.utility.verify_payment_signature(params_dict)
            except razorpay.errors.SignatureVerificationError:
                return JsonResponse(
                    {"success": False, "message": "Invalid payment signature"},
                    status=400
                )
            
            user = request.user
            course = Course.objects.get(id=course_id)
            
            # Save payment details
            payment = Payment.objects.create(
                user=user,
                course=course,
                amount=data.get("amount", 0),
                method=data.get("method", "unknown"),
                transaction_id=data.get("transaction_id"),
                status="success",
            )
            
            # Enroll user in course
            Enrollment.objects.create(
                user=user,
                course=course,
                payment=True,
                status="active"
            )

            StudentCourseProgress.objects.create(
                student=user,
                course=course,
                completed_lessons_count=0,
                progress=0.00,
                is_completed=False
            )
            
            # Update monthly stats
            self._update_monthly_stats(course)
            
            return JsonResponse(
                {"success": True, "message": "Payment verified successfully!"}
            )
        
        except Course.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "Course not found"},
                status=404
            )
        except Exception as e:
            return JsonResponse(
                {"success": False, "error": str(e)},
                status=500
            )
    
    def _update_monthly_stats(self, course):
        """Helper method to update monthly enrollment statistics."""
        INSTRUCTOR_PERCENT = Decimal('0.60')
        PLATFORM_PERCENT = Decimal('0.40')
        today = date.today()
        month_start = today.replace(day=1)
        course_price = Decimal(course.price)

        stats, created = MonthlyCourseStats.objects.get_or_create(
            instructor=course.instructor,
            course=course,
            month=month_start,
            defaults={
                "total_enrollments": 1,
                "total_amount": course_price,
                "instructor_share": course_price * INSTRUCTOR_PERCENT,
                "platform_share": course_price * PLATFORM_PERCENT,
            }
        )

        if not created:
            stats.total_enrollments += 1
            stats.total_amount += course_price
            stats.instructor_share += course_price * INSTRUCTOR_PERCENT
            stats.platform_share += course_price * PLATFORM_PERCENT
            stats.save()


class InstructorMonthlyStatsView(APIView):
    """
    API endpoint to retrieve monthly stats for an instructor.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, instructor_id):
        """
        Get last 5 monthly stats records for an instructor.
        
        Args:
            instructor_id: ID of the instructor
            
        Returns:
            Response: Serialized monthly stats data
        """
        try:
            stats = MonthlyCourseStats.objects.filter(
                instructor=instructor_id
            ).order_by('-month')[:5]
            serializer = MonthlyCourseStatsSerializer(stats, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentListView(generics.ListAPIView):
    """
    API endpoint to list all payments ordered by creation date.
    """
    queryset = Payment.objects.all().order_by('-created_at')
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]


class InstructorEnrollmentStats(APIView):
    """
    API endpoint for enrollment statistics by instructor.
    """
    def get(self, request, instructor_id):
        """
        Get enrollment counts by month for an instructor's courses.
        
        Args:
            instructor_id: ID of the instructor
            
        Returns:
            Response: Enrollment statistics data
        """
        try:
            enrollments = (
                Enrollment.objects
                .filter(course__instructor_id=instructor_id)
                .annotate(month=TruncMonth('enrolled_at'))
                .values('course__title', 'course__price', 'month')
                .annotate(enrollment_count=Count('id'))
                .order_by('month')
            )
            return Response(enrollments)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InstructorPayoutSummary(APIView):
    """
    API endpoint for instructor payout summary for previous month.
    """
    def get(self, request, instructor_id):
        """
        Get payment summary for an instructor for the previous month.
        
        Returns:
            Response: {
                "month": "April 2023",
                "total_amount": 1000.00,
                "instructor_share": 600.00,
                "platform_share": 400.00
            }
        """
        today = date.today()
        first_day_of_prev_month = date(today.year, today.month, 1) - relativedelta(months=1)
        
        previous_month_stats = MonthlyCourseStats.objects.filter(
            instructor_id=instructor_id,
            month=first_day_of_prev_month
        )
        
        if not previous_month_stats.exists():
            return Response(
                {
                    "detail": f"No records for {first_day_of_prev_month.strftime('%B %Y')}",
                    "month": first_day_of_prev_month.strftime('%B %Y'),
                    "total_amount": 0,
                    "instructor_share": 0,
                    "platform_share": 0
                },
                status=status.HTTP_200_OK
            )
        
        aggregates = previous_month_stats.aggregate(
            total_amount=Sum('total_amount') or 0,
            instructor_share=Sum('instructor_share') or 0,
            platform_share=Sum('platform_share') or 0
        )
        
        return Response({
            "month": first_day_of_prev_month.strftime('%B %Y'),
            "total_amount": float(aggregates['total_amount']),
            "instructor_share": float(aggregates['instructor_share']),
            "platform_share": float(aggregates['platform_share'])
        })


class InstructorPayoutCreateView(APIView):
    """
    API endpoint for creating instructor payouts.
    """
    def post(self, request):
        """
        Create a payout record and update monthly stats.
        
        Args:
            request: Contains payout details
            
        Returns:
            Response: Created payout data or errors
        """
        serializer = InstructorPayoutSerializer(data=request.data)
        if serializer.is_valid():
            payout = serializer.save()
            
            # Update monthly stats
            MonthlyCourseStats.objects.filter(
                instructor=payout.instructor.id,
                month__year=payout.month.year,
                month__month=payout.month.month
            ).update(
                paid_to_instructor=True,
                paid_on=payout.month
            )
            
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class InstructorPayoutStatusView(APIView):
    """
    API endpoint to check payout status for an instructor in a specific month.
    """
    def get(self, request, instructor_id, date_str):
        """
        Get payout status for instructor in specified month.
        
        Args:
            date_str: Date in YYYY-MM-DD format (day is ignored)
            
        Returns:
            Response: Payout details or error message
        """
        try:
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            payout = InstructorPayout.objects.get(
                instructor__id=instructor_id,
                month__year=parsed_date.year,
                month__month=parsed_date.month
            )
            
            serializer = InstructorPayoutSerializer(payout)
            return Response(serializer.data)
            
        except ValueError:
            return Response(
                {"detail": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except InstructorPayout.DoesNotExist:
            return Response(
                {"detail": f"No payout record found for {parsed_date.strftime('%B %Y')}."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )