from django.contrib import admin
from .models import Course, Track, TrackCourse, GraduationRequirement, AreaRequirement, TakenCourse

admin.site.register(Course)
admin.site.register(Track)
admin.site.register(TrackCourse)
admin.site.register(GraduationRequirement)
admin.site.register(AreaRequirement)
admin.site.register(TakenCourse)
