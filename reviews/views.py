from django.shortcuts import render
from rest_framework import generics, permissions,serializers 
from rest_framework import status
from .models import Review
from .serializers import ReviewSerializer
from rest_framework.response import Response

class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self,request,*args,**kwargs):
        try:
            return super().create(request,*args,**kwargs)
        except serializers.ValidationError as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)    



class ReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except serializers.ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)