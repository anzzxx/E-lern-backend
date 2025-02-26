from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Instructor

@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "experience", "organisation", "created_at")
    search_fields = ("name", "phone", "experience", "organisation")
    list_filter = ("created_at", "updated_at")
    ordering = ("-created_at",)

