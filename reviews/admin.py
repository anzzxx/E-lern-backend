from django.contrib import admin

from django.contrib import admin
from .models import Review

class ReviewAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('user', 'course', 'rating', 'created_at', 'short_comment')
    
    # Add search functionality
    search_fields = ('user__username', 'course__title', 'comment')
    
    # Add filters
    list_filter = ('rating', 'created_at', 'course')
    
    # Make the list view sortable
    ordering = ('-created_at',)
    
    # Fields to display in the edit view
    fieldsets = (
        (None, {
            'fields': ('user', 'course', 'rating')
        }),
        ('Additional Information', {
            'fields': ('comment',),
            'classes': ('collapse',)
        }),
    )
    
    # Custom method to display shortened comment
    def short_comment(self, obj):
        if obj.comment:
            return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
        return ""
    short_comment.short_description = 'Comment Preview'

# Register your model with the custom admin class
admin.site.register(Review, ReviewAdmin)
