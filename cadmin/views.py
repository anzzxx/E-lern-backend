from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer
from accounts.models import CustomUser
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import authenticate, get_user_model
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from Courses.models import Course
from .serializers import CourseSerializer




class SuperUserOnly(permissions.BasePermission):
    """ Custom permission to allow only superusers to access this view. """
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser  # Allow only superusers

class UserListView(generics.ListAPIView):
    """ Retrieve all users (Superuser access only) """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [SuperUserOnly]  # Restrict to superusers

class UserUpdateView(generics.UpdateAPIView):
    """ Update a user's is_active status (Superuser access only) """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [SuperUserOnly]  # Restrict to superusers
    lookup_field = "id"  # Allow updating user by ID

    def patch(self, request, *args, **kwargs):
        """ Handle PATCH requests to update is_active field """
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



User = get_user_model()  # Get the custom user model

class SuperuserLoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Both email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate user with email (CustomUser uses email as USERNAME_FIELD)
        user = authenticate(request, email=email, password=password)

        if user is None or not user.is_superuser:
            return Response({"error": "Invalid credentials or not a superuser"}, status=status.HTTP_403_FORBIDDEN)

        # Generate JWT tokens (both access & refresh)
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token  # Generate access token from refresh

        access["is_superuser"] = user.is_superuser  # Add is_superuser flag to payload
        access["is_staff"] = user.is_staff  # Add is_staff flag to payload


        return Response(
            {
                "refresh": str(refresh),
                "access": str(access),
                "is_superuser": user.is_superuser,
                "is_staff": user.is_staff,
            },
            status=status.HTTP_200_OK,
        )


# Custom permission to allow only superusers
class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

# API to get all inactive courses (Only superusers can access)
class InactiveCourseListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSuperUser]

    def get(self, request):
        courses = Course.objects.filter(is_active=False)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# API to activate a course (Only superusers can modify)
class ActivateCourseView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSuperUser]

    def patch(self, request, pk):
        try:
            course = Course.objects.get(pk=pk, is_active=False)
            course.is_active = True
            course.save()
            return Response({"message": "Course activated successfully!"}, status=status.HTTP_200_OK)
        except Course.DoesNotExist:
            return Response({"error": "Course not found or already active"}, status=status.HTTP_404_NOT_FOUND)


