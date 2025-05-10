from django.contrib import admin
from django.contrib import admin
from .models import Course, Enrollment, CourseReport,StudentCourseProgress


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'price', 'status', 'created_at')
    search_fields = ('title', 'instructor__user__username')
    list_filter = ('status', 'is_active', 'created_at')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'payment', 'status', 'progress', 'enrolled_at')
    search_fields = ('user__username', 'course__title')
    list_filter = ('status', 'payment')
    readonly_fields = ('enrolled_at',)  # Prevents editing but allows viewing

@admin.register(CourseReport)
class CourseReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'status', 'created_at')
    search_fields = ('user__username', 'course__title')
    list_filter = ('status', 'created_at')
admin.site.register(StudentCourseProgress)

# Alternative method (if no customization is needed):
# admin.site.register(Course)
# admin.site.register(Enrollment)
# admin.site.register(CourseReport)

