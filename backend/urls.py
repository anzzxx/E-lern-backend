
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
   
] +static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

