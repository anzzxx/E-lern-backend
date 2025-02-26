# Generated by Django 5.1.6 on 2025-02-24 13:33

import cloudinary.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Courses', '0002_remove_course_category_course_preview_video_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='preview_video',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='thumbnail',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image'),
        ),
    ]
