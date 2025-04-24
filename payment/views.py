from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import razorpay
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Payment,MonthlyCourseStats
from accounts.models import CustomUser as User
from Courses.models import Course, Enrollment,StudentCourseProgress
from .serializers import *
from django.db.models.functions import TruncMonth
from django.db.models import Count
from rest_framework.response import Response
from decimal import Decimal
from rest_framework import status
from datetime import date, timedelta
from .models import MonthlyCourseStats
from teacher.models import Instructor
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from .models import MonthlyCourseStats, Instructor
from django.db.models import Sum
import calendar
from dateutil.relativedelta import relativedelta
from .models import InstructorPayout

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

class CreatePaymentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            data = request.data
            amount = int(data.get("amount", 0)) * 100  # Convert to paisa
            course_id = data.get("course_id")
            user_id = request.user.id
            
            if not amount or not course_id:
                return JsonResponse({"success": False, "message": "Missing required fields"}, status=400)
            
            print(f"Creating order for User: {user_id}, Course: {course_id}, Amount: {amount}")
            
            order_data = {
                "amount": amount,
                "currency": "INR",
                "payment_capture": "1",
            }
            
            order = razorpay_client.order.create(order_data)
            return JsonResponse(order)
        
        except Exception as e:
            print(f"Error creating order: {e}")
            return JsonResponse({"success": False, "error": str(e)}, status=500)


class WebhookView(APIView):
    def post(self, request):
        payload = request.body
        signature = request.headers.get("X-Razorpay-Signature")
        
        try:
            razorpay_client.utility.verify_webhook_signature(payload, signature, settings.RAZORPAY_KEY_SECRET)
            data = json.loads(payload)
            print(f"Webhook Payment Success: {json.dumps(data, indent=4)}")
            return JsonResponse({"status": "success"})
        
        except Exception as e:
            print(f"Webhook verification failed: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=400)


class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            data = request.data
            payment_id = data.get("payment_id")
            order_id = data.get("order_id")
            signature = data.get("signature")
            course_id = data.get("course_id")
            transaction_id = data.get("transaction_id")
            payment_method = data.get("method")
            status = data.get("status")
            
            if not payment_id or not order_id or not signature:
                return JsonResponse({"success": False, "message": "Missing payment details"}, status=400)
            
            params_dict = {
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }
            
            try:
                razorpay_client.utility.verify_payment_signature(params_dict)
                payment_verified = True
            except razorpay.errors.SignatureVerificationError as e:
                return JsonResponse({"success": False, "message": "Invalid payment signature"}, status=400)
            
            if payment_verified:
                user = request.user
                course = Course.objects.get(id=course_id)
                
                # Save payment details in the database
                payment = Payment.objects.create(
                    user=user,
                    course=course,
                    amount=data.get("amount", 0),
                    method=payment_method or "unknown",
                    transaction_id=transaction_id,
                    status="success",
                )
                
                # Enroll user in the course after successful payment
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
                # Assume 60% instructor, 40% platform
                INSTRUCTOR_PERCENT = Decimal('0.60')
                PLATFORM_PERCENT = Decimal('0.40')

                today = date.today()
                month_start = today.replace(day=1)

                instructor = course.instructor
                course_price = Decimal(course.price)
      
                stats, created = MonthlyCourseStats.objects.get_or_create(
                    instructor=instructor,
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
                
                return JsonResponse({"success": True, "message": "Payment verified successfully!"})
        
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
        
        return JsonResponse({"success": False, "message": "Invalid request"}, status=400)



class InstructorMonthlyStatsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, instructor_id):
        try:
            stats = MonthlyCourseStats.objects.filter(instructor=instructor_id).order_by('-month')[:5]
            serializer = MonthlyCourseStatsSerializer(stats, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except MonthlyCourseStats.DoesNotExist:
            return Response({"error": "Instructor not found or no data available."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentListView(generics.ListAPIView):
    queryset = Payment.objects.all().order_by('-created_at')
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
class InstructorEnrollmentStats(APIView):
    
    def get(self,request,instructor_id):
        enrollments=(
            Enrollment.objects
            .filter(course__instructor_id=instructor_id)
            .annotate(month=TruncMonth('enrolled_at'))
            .values('course__title','course__price','month')
            .annotate(enrollment_count=Count('id'))
            .order_by('month')
            
        )    
        try:
            return Response(enrollments)
        except:
            return Response({error:"some error occourd"})



class InstructorPayoutSummary(APIView):
    def get(self, request, instructor_id):
        """
        Get payment summary for an instructor for the previous month
        Returns:
        {
            "month": "April 2023",
            "total_amount": 1000.00,
            "instructor_share": 600.00,
            "platform_share": 400.00
        }
        """
        # Calculate previous month
        today = date.today()
        first_day_of_prev_month = date(today.year, today.month, 1) - relativedelta(months=1)
        
        # Get all records for the instructor from previous month
        previous_month_stats = MonthlyCourseStats.objects.filter(
            instructor_id=instructor_id,
            month=first_day_of_prev_month
        )
        
        # If no records found
        if not previous_month_stats.exists():
            return Response(
                {
                    "detail": f"No payment records found for {first_day_of_prev_month.strftime('%B %Y')}",
                    "month": first_day_of_prev_month.strftime('%B %Y'),
                    "total_amount": 0,
                    "instructor_share": 0,
                    "platform_share": 0
                },
                status=status.HTTP_200_OK
            )
        
        # Calculate totals by summing all records
        total_amount = previous_month_stats.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        instructor_share = previous_month_stats.aggregate(
            total=Sum('instructor_share')
        )['total'] or 0
        
        platform_share = previous_month_stats.aggregate(
            total=Sum('platform_share')
        )['total'] or 0
        
        # Format response
        response_data = {
            "month": first_day_of_prev_month.strftime('%B %Y'),
            "total_amount": float(total_amount),
            "instructor_share": float(instructor_share),
            "platform_share": float(platform_share)
        }
        
        return Response(response_data, status=status.HTTP_200_OK)



class InstructorPayoutCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = InstructorPayoutSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            instructor = serializer.validated_data.get('instructor')
            month = serializer.validated_data.get('month')
            given_date = month  
            ev=MonthlyCourseStats.objects.filter(
                instructor=instructor.id,
                month__year=given_date.year,
                month__month=given_date.month
            ).update(
                paid_to_instructor=True,
                paid_on=given_date
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InstructorPayoutStatusView(APIView):
    def get(self, request, instructor_id, date):
        try:
            # Parse the date string (format: YYYY-MM-DD) into a date object
            # We only need year and month, so day can be ignored or set to 1
            parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
            year = parsed_date.year
            month = parsed_date.month
            
            # Get the payout record for the instructor and month
            # We'll query for any date in that month (using __year and __month lookups)
            payout = InstructorPayout.objects.get(
                instructor__id=instructor_id,
                month__year=year,
                month__month=month
            )
            
            serializer = InstructorPayoutSerializer(payout)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ValueError:
            return Response(
                {"detail": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except InstructorPayout.DoesNotExist:
            return Response(
                {"detail": f"No payout record found for instructor {instructor_id} in {parsed_date.strftime('%B %Y')}."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )