
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/",include("accounts.urls")),
    path('instructor/', include('teacher.urls')),
    path('course/',include('Courses.urls')),
    path('cadmin/',include('cadmin.urls')),
    path('lessons/',include('Lessons.urls')),
    path('notifications/', include('notifications.urls')),
    path('chat/', include('chat.urls')),
    path('payment/', include('payment.urls')),
    path('reviews/', include('reviews.urls')),
    path('mcq/', include('mcqtest.urls')),
   
   
] +static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

