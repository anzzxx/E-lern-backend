from django.contrib import admin
from .models import CustomUser
from .forms import CustomUserCreationForm,CustomUserChangeForm
from django.contrib.auth.admin import UserAdmin
# Register your models here.

@admin.register(CustomUser)
class CustomAdminUser(UserAdmin):
    add_form=CustomUserCreationForm
    form=CustomUserChangeForm

    model=CustomUser
