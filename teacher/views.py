from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions,status
from rest_framework.permissions import IsAuthenticated
from .serializers import InstructorSerializer,InstructorListSerializer
from .models import Instructor
from rest_framework import serializers
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound



class CreateInstructorView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            if Instructor.objects.filter(user=request.user).exists():
                return Response({"error": "Instructor profile already exists"}, status=status.HTTP_400_BAD_REQUEST)

            serializer = InstructorSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                user = request.user
                user.is_staff = True
                user.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class RetriveInstructorView(generics.ListAPIView):
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer
    permission_classes = [permissions.IsAdminUser]
         


class RetrieveInstructorProfile(generics.RetrieveAPIView):
    serializer_class = InstructorListSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    lookup_url_kwarg = 'instructorId'

    def get_object(self):
        instructor_id = self.kwargs.get(self.lookup_url_kwarg)
        try:
            return Instructor.objects.get(id=instructor_id)
        except Instructor.DoesNotExist:
            raise NotFound(detail="Instructor profile not found.")





class InstructorDetailByUserView(APIView):
    def get(self, request, user_id):
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
