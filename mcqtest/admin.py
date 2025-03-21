
from django.contrib import admin
from .models import Test, Question, Answer

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'course')  # Display these fields in the admin list view
    search_fields = ('title', 'course__name')  # Enable search functionality

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'test')
    search_fields = ('text',)

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct')
    list_filter = ('is_correct',)

