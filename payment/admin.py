from django.contrib import admin
from .models import Payment, MonthlyCourseStats, InstructorPayout


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'course', 'amount', 'method', 'status', 'created_at')
    search_fields = ('transaction_id', 'user__email', 'course__title')
    list_filter = ('status', 'method', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(MonthlyCourseStats)
class MonthlyCourseStatsAdmin(admin.ModelAdmin):
    list_display = ('course', 'instructor', 'month', 'total_enrollments', 'total_amount', 'instructor_share', 'platform_share', 'paid_to_instructor', 'paid_on')
    list_filter = ('month', 'paid_to_instructor')
    search_fields = ('course__title', 'instructor__user__username')


@admin.register(InstructorPayout)
class InstructorPayoutAdmin(admin.ModelAdmin):
    list_display = ('instructor', 'month', 'total_amount', 'payout_method', 'is_paid', 'paid_on')
    list_filter = ('month', 'is_paid')
    search_fields = ('instructor__user__username', 'payout_reference')

