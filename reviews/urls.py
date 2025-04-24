from django.urls import path
from .views import *

urlpatterns = [
    path('create/', ReviewCreateView.as_view(), name='review-create'),
    path('retrive/',ReviewListView.as_view(), name='review-retrive'),
    path('edit-update/<int:pk>/', ReviewEditDeleteView.as_view(), name='review-edit-delete'),
]
