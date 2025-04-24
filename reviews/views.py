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

class ReviewEditDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only allow the authenticated user to access their own reviews
        return Review.objects.filter(user=self.request.user)

    def put(self, request, *args, **kwargs):
        try:
            return self.update(request, *args, **kwargs)
        except serializers.ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        review = self.get_object()
        if review.user != request.user:
            return Response({'error': 'You do not have permission to delete this review.'}, status=status.HTTP_403_FORBIDDEN)
        return self.destroy(request, *args, **kwargs)

class ReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except serializers.ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)