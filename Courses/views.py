from rest_framework import generics, status ,permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import Course,CourseReport
from .serializers import *
from .models import Enrollment,CourseReport,StudentCourseProgress
from teacher.models import Instructor
from .serializers import CourseSerializer,CourseReportViewSerializer
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import IsAuthenticated

class CourseListView(generics.ListCreateAPIView):
    """
    API view to list spesific courses for the instructor
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    parser_classes = [MultiPartParser, FormParser] 
    permission_classes = [permissions.IsAuthenticated] 
    
    def get_queryset(self):
        instructor = Instructor.objects.get(user=self.request.user)
        if instructor:
            return Course.objects.filter(instructor=instructor) 
        return Course.objects.none()
    


class ReportCourseDetailsView(generics.RetrieveAPIView):
    """
    Retrieve a specific course report by report ID and course ID for admin only.
    """
    serializer_class = CourseReportViewSerializer
    # permission_classes = [IsAdminUser]

    def get_object(self):
        course_id = self.kwargs.get("courseId")
        report_id = self.kwargs.get("reportId")
        return CourseReport.objects.select_related('user', 'course', 'course__instructor__user').get(
            id=report_id,
            course__id=course_id
        )

        
class CourseAllListView(generics.ListAPIView):
    """
    API view to list all courses with a custom response format.
    """
    queryset = Course.objects.filter(is_active=True)
    serializer_class = CourseSerializer
    

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                "status": True,
                "message": "Courses fetched successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False,
                "message": "An error occurred while fetching courses.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CourseCreateView(generics.CreateAPIView):
    """creating new course """
    serializer_class = CourseSerializer
    parser_classes = [MultiPartParser, FormParser] 
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(
                {
                    "success": True,
                    "message": "Course created successfully!",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "success": False,
                "message": "Course creation failed",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, and delete a course.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    parser_classes = [MultiPartParser, FormParser]

    def retrieve(self, request, *args, **kwargs):
        user = request.user 
        instructor=Instructor.objects.get(user=user)
        courses = Course.objects.filter(instructor=instructor) 
        serializer = self.get_serializer(courses, many=True) 
        return Response(
            {
                "success": True,
                "message": "Course details retrieved successfully!",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(
                {
                    "success": True,
                    "message": "Course updated successfully!",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "Course update failed",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {
                "success": True,
                "message": "Course deleted successfully!",
            },
            status=status.HTTP_204_NO_CONTENT,
        )




class UserEnrolledCoursesView(generics.ListAPIView):
    """
    API endpoint that returns all courses enrolled by the current user
    """
    serializer_class = EnrolledCourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get all published courses the user is enrolled in
        return Course.objects.filter(
            enrollments__user=self.request.user,
            is_active=True
        ).select_related('instructor').order_by('-enrollments__enrolled_at')

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            
            return Response({
                'success': True,
                'count': queryset.count(),
                'courses': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Failed to fetch enrolled courses',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)       
class CourseRetriveView(generics.RetrieveAPIView):
   
   pass


class CourseReportCreateView(generics.CreateAPIView):
    queryset = CourseReport.objects.all()
    serializer_class = CourseReportSerializer
    permission_classes = [permissions.IsAuthenticated]  



class CourseReportListView(generics.ListAPIView):
    queryset = CourseReport.objects.all()
    serializer_class = CourseReportSerializer
    permission_classes = [permissions.IsAdminUser]

class StudentsProgressListView(generics.ListAPIView):
    serializer_class = StudentsProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter records related to the logged-in user
        return StudentCourseProgress.objects.filter(student=self.request.user)