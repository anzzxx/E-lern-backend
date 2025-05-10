from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate, get_user_model
from django.db.models import Sum, F, Count, Avg
from django.db.models.functions import TruncMonth
from django.utils.timezone import now
import calendar

from .serializers import *
from accounts.models import CustomUser
from Courses.models import Course, Enrollment, StudentCourseProgress
from reviews.models import Review
from notifications.models import Notification
from rest_framework.permissions import IsAdminUser

User = get_user_model()

class SuperUserOnly(permissions.BasePermission):
    """Allows access only to superusers."""
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser  


class UserListView(generics.ListAPIView):
    """View to list all users (superuser only)."""
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [SuperUserOnly]


class UserUpdateView(generics.UpdateAPIView):
    """View to update a user's `is_active` status (superuser only)."""
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [SuperUserOnly]
    lookup_field = "id"

    def patch(self, request, *args, **kwargs):
        """Handles PATCH requests to update a user."""
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SuperuserLoginView(APIView):
    """Authenticates a superuser and returns JWT tokens."""
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Both email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)

        if user is None or not user.is_superuser:
            return Response({"error": "Invalid credentials or not a superuser"}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        access["is_superuser"] = user.is_superuser
        access["is_staff"] = user.is_staff

        return Response({
            "refresh": str(refresh),
            "access": str(access),
            "is_superuser": user.is_superuser,
            "is_staff": user.is_staff,
        }, status=status.HTTP_200_OK)


class IsSuperUser(permissions.BasePermission):
    """Permission class to check for superuser access."""
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class InactiveCourseListView(APIView):
    """Returns a list of inactive courses."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSuperUser]

    def get(self, request):
        courses = Course.objects.filter(is_active=False).order_by('-created_at')
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ActivateCourseView(APIView):
    """Activates an inactive course and sends notifications."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        try:
            course = Course.objects.get(pk=pk, is_active=False)
            course.is_active = True
            course.save()

            sender = request.user
            recipients = CustomUser.objects.filter(is_active=True)
            message = f"Course is created successfully! Enjoy the course {course.title}."

            notifications = [
                Notification(sender=sender, recipient=recipient, message=message)
                for recipient in recipients
            ]
            Notification.objects.bulk_create(notifications)

            return Response({"message": "Course activated successfully, notifications sent!"}, status=status.HTTP_200_OK)

        except Course.DoesNotExist:
            return Response({"error": "Course not found or already active"}, status=status.HTTP_404_NOT_FOUND)


class TotalEnrolledStudentsAPIView(APIView):
    """Returns the total number of enrolled students."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        count = Enrollment.objects.count()
        serializer = TotalEnrolledStudentsSerializer({'total_enrolled': count})
        return Response(serializer.data)


class TotalRevenueAPIView(APIView):
    """Returns the total revenue generated from paid enrollments."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_revenue = Enrollment.objects.filter(payment=True).aggregate(
            total=Sum(F('course__price'))
        )['total'] or 0

        data = {'total_revenue': total_revenue}
        serializer = TotalRevenueSerializer(data)
        return Response(serializer.data)


class MonthlyRevenueAPIView(APIView):
    """Provides monthly analytics for revenue, enrollments, courses created, and completions."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            current_year = now().year
            current_month = now().month

            revenue_data = (
                Enrollment.objects.filter(payment=True, enrolled_at__year=current_year)
                .annotate(month=TruncMonth('enrolled_at'))
                .values('month')
                .annotate(revenue=Sum(F('course__price')))
                .order_by('month')
            )
            revenue_by_month = {entry['month'].month: float(entry['revenue']) for entry in revenue_data}

            enrollment_data = (
                Enrollment.objects.filter(payment=True, enrolled_at__year=current_year)
                .annotate(month=TruncMonth('enrolled_at'))
                .values('month')
                .annotate(count=Count('id'))
                .order_by('month')
            )
            enrollment_by_month = {entry['month'].month: entry['count'] for entry in enrollment_data}

            course_data = (
                Course.objects.filter(created_at__year=current_year)
                .annotate(month=TruncMonth('created_at'))
                .values('month')
                .annotate(count=Count('id'))
                .order_by('month')
            )
            course_by_month = {entry['month'].month: entry['count'] for entry in course_data}

            completed_students_data = (
                StudentCourseProgress.objects.filter(is_completed=True, updated_at__year=current_year)
                .annotate(month=TruncMonth('updated_at'))
                .values('month')
                .annotate(count=Count('id'))
                .order_by('month')
            )
            completed_by_month = {entry['month'].month: entry['count'] for entry in completed_students_data}

            result = {}
            for month in range(1, current_month + 1):
                month_name = calendar.month_name[month]
                result[month_name] = {
                    'revenue': revenue_by_month.get(month, 0.00),
                    'created_course_count': course_by_month.get(month, 0),
                    'enrollment_count': enrollment_by_month.get(month, 0),
                    'completed_student_count': completed_by_month.get(month, 0)
                }

            return Response(result)

        except Exception as e:
            return Response({"error": "An error occurred while processing data."}, status=500)


class CourseAnalyticsView(APIView):
    """Returns analytics for each course including enrollments, average rating, revenue, and status."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        courses = Course.objects.all()
        results = []

        for course in courses:
            enrollments = Enrollment.objects.filter(course=course)
            total_enrollment = enrollments.count()
            avg_review = Review.objects.filter(course=course).aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0.0
            revenue = enrollments.filter(payment=True).aggregate(total=Sum('course__price'))['total'] or 0.0

            results.append({
                "title": course.title,
                "total_enrollment": total_enrollment,
                "avg_review": round(avg_review, 2),
                "revenue": revenue,
                "is_active": course.is_active
            })

        serializer = CourseAnalyticsSerializer(results, many=True)
        return Response(serializer.data)
