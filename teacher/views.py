from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import InstructorSerializer
from .models import Instructor

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