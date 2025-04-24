from django.contrib import admin
from .models import CustomUser
from .forms import CustomUserCreationForm,CustomUserChangeForm
from django.contrib.auth.admin import UserAdmin


@admin.register(CustomUser)
class CustomAdminUser(UserAdmin):
    add_form=CustomUserCreationForm
    form=CustomUserChangeForm

    model=CustomUser
