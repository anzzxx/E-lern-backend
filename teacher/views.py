from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from payment.models import InstructorPayout
from rest_framework import serializers
from rest_framework.generics import ListAPIView
from rest_framework.exceptions import NotFound
from django.db.models import Sum, Count, Case, When, Value, IntegerField
from Courses.models import Enrollment, Course
from reviews.models import Review
from django.db.models import Avg
from django.db.models.functions import TruncMonth
from datetime import datetime
import calendar


class CreateInstructorView(APIView):
    """API view for creating an instructor profile."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Create an instructor profile for the authenticated user.
        
        Returns:
            - 201 Created if profile is created successfully
            - 400 Bad Request if profile already exists or data is invalid
            - 500 Internal Server Error for other exceptions
        """
        try:
            if Instructor.objects.filter(user=request.user).exists():
                return Response(
                    {"error": "Instructor profile already exists"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = InstructorSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                user = request.user
                user.is_staff = True
                user.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RetriveInstructorView(generics.ListAPIView):
    """API view to retrieve all instructor profiles."""
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer


class RetrieveInstructorProfile(generics.RetrieveAPIView):
    """API view to retrieve a specific instructor profile."""
    serializer_class = InstructorListSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    lookup_url_kwarg = 'instructorId'

    def get_object(self):
        """
        Get instructor profile by ID.
        
        Raises:
            NotFound: If instructor with given ID doesn't exist
        """
        instructor_id = self.kwargs.get(self.lookup_url_kwarg)
        try:
            return Instructor.objects.get(id=instructor_id)
        except Instructor.DoesNotExist:
            raise NotFound(detail="Instructor profile not found.")


class InstructorDetailByUserView(APIView):
    """API view to get instructor details by user ID."""

    def get(self, request, user_id):
        """
        Retrieve instructor details for the given user ID.
        
        Returns:
            - 200 OK with instructor data if found
            - 404 Not Found if instructor doesn't exist
            - 500 Internal Server Error for other exceptions
        """
        try:
            instructor = Instructor.objects.get(user_id=user_id)
            serializer = InstructorSerializer(instructor)
            return Response({
                'message': 'Instructor details fetched successfully.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Instructor.DoesNotExist:
            return Response({
                'message': 'Instructor with the given user ID does not exist.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'message': 'An error occurred while fetching the instructor.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InstructorPayoutStatsView(APIView):
    """API view to get payout statistics for the authenticated instructor."""

    def get(self, request):
        """
        Retrieve payout statistics including total revenue and payout counts.
        
        Returns:
            - 200 OK with statistics data if instructor exists
            - 404 Not Found if instructor doesn't exist
        """
        try:
            instructor = Instructor.objects.get(user=request.user)
            
            # Calculate stats
            stats = InstructorPayout.objects.filter(
                instructor=instructor
            ).aggregate(
                total_revenue=Sum('total_amount'),
                payout_count=Count('id'),
                paid_payout_count=Sum(
                    Case(
                        When(is_paid=True, then=Value(1)),
                        default=Value(0),
                        output_field=IntegerField()
                    )
                ),
                unpaid_payout_count=Sum(
                    Case(
                        When(is_paid=False, then=Value(1)),
                        default=Value(0),
                        output_field=IntegerField()
                    )
                )
            )
            
            # Prepare response data
            data = {
                'instructor_id': instructor.id,
                'instructor_name': instructor.user.username,
                'total_revenue': stats['total_revenue'] or 0,
                'payout_count': stats['payout_count'] or 0,
                'paid_payout_count': stats['paid_payout_count'] or 0,
                'unpaid_payout_count': stats['unpaid_payout_count'] or 0,
            }
            
            serializer = InstructorPayoutStatsSerializer(data)
            return Response(serializer.data)
            
        except Instructor.DoesNotExist:
            return Response(
                {'error': 'Instructor not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class InstructorStudentListView(APIView):
    """API view to list all students enrolled in instructor's courses."""

    def get(self, request):
        """
        Get list of unique students enrolled in the instructor's courses.
        
        Returns:
            - 200 OK with student list if instructor exists
            - 404 Not Found if instructor doesn't exist
        """
        try:
            instructor = Instructor.objects.get(user=request.user)
            enrolled_courses = Enrollment.objects.filter(
                course__instructor__id=instructor.id
            )
            students = list({enrollment.user for enrollment in enrolled_courses})

            serializer = InstructorStudentListSerializer(students, many=True)
            return Response(serializer.data)

        except Instructor.DoesNotExist:
            return Response(
                {'error': 'Instructor not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class InstructorAvgCourseRatingView(APIView):
    """API view to get average rating of instructor's courses."""

    def get(self, request):
        """
        Calculate and return average rating for all instructor's courses.
        
        Returns:
            - 200 OK with average rating if instructor exists
            - 404 Not Found if instructor doesn't exist
        """
        try:
            instructor = Instructor.objects.get(user=request.user)
            avg_rating = Review.objects.filter(
                course__instructor__id=instructor.id
            ).aggregate(avg_rating=Avg('rating'))
            serializer = InstructorAvgRatingSerializer(avg_rating)
            return Response(serializer.data)

        except Instructor.DoesNotExist:
            return Response(
                {'error': 'Instructor not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class InstructorSalesDataView(APIView):
    """API view to get monthly sales data for the current year."""

    def get(self, request):
        """
        Retrieve monthly sales data (purchases and earnings) for current year.
        
        Returns:
            - 200 OK with sales data if instructor exists
            - 404 Not Found if instructor doesn't exist
        """
        try:
            current_year = datetime.now().year
            current_month = datetime.now().month
        
            instructor = Instructor.objects.get(user=request.user)
            instructor_courses = Course.objects.filter(instructor_id=instructor.id)
        
            enrollments = Enrollment.objects.filter(
                course__in=instructor_courses,
                enrolled_at__year=current_year,
                payment=True
            ).annotate(
                month=TruncMonth('enrolled_at')
            ).values('month').annotate(
                purchases=Count('id'),
                earnings=Sum('course__price') 
            ).order_by('month')
        
            existing_months = {e['month'].month: e for e in enrollments}
        
            sales_data = []
            for month_num in range(1, current_month + 1):
                month_name = calendar.month_abbr[month_num]
                if month_num in existing_months:
                    sales_data.append({
                        'month': month_name,
                        'year': current_year,
                        'purchases': existing_months[month_num]['purchases'],
                        'earnings': existing_months[month_num]['earnings']
                    })
                else:
                    sales_data.append({
                        'month': month_name,
                        'year': current_year,
                        'purchases': 0,
                        'earnings': 0
                    })
        
            serializer = SalesDataSerializer(sales_data, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Instructor.DoesNotExist:
            return Response(
                {'error': 'Instructor not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class InstructorCourseSalesView(ListAPIView):
    """API view to list all sales for instructor's courses."""
    serializer_class = InstructorSalesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Get enrollments for all courses belonging to the authenticated instructor.
        
        Returns:
            QuerySet of enrollments or empty queryset if not authenticated or not instructor
        """
        user = self.request.user
        if not user.is_authenticated:
            return Enrollment.objects.none()
        try:
            instructor = Instructor.objects.get(user=user)
            return Enrollment.objects.filter(
                course__instructor=instructor
            ).order_by('-enrolled_at')
        except Instructor.DoesNotExist:
            return Enrollment.objects.none()