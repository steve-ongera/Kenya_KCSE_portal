from django.contrib import admin
from .models import (
    County, School, Student, Subject, 
    ExaminationSession, StudentMarks, 
    StudentOverallPerformance
)
from .models import *

@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'school_code', 'county')
    search_fields = ('name', 'school_code')
    list_filter = ('county',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'index_number', 'school', 'gender')
    search_fields = ('first_name', 'last_name', 'index_number')
    list_filter = ('school', 'gender')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category')
    list_filter = ('category',)

@admin.register(ExaminationSession)
class ExaminationSessionAdmin(admin.ModelAdmin):
    list_display = ('year', 'start_date', 'end_date')

@admin.register(StudentMarks)
class StudentMarksAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'examination_session', 'score', 'grade')
    list_filter = ('subject', 'examination_session', 'grade')
    search_fields = ('student__index_number', 'student__first_name', 'student__last_name')

@admin.register(StudentOverallPerformance)
class StudentOverallPerformanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'examination_session', 'total_score', 'mean_grade')
    list_filter = ('examination_session', 'mean_grade')
    search_fields = ('student__index_number',)


class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_at', 'updated_at', 'is_active', 'views')
    search_fields = ('title', 'description')
    list_filter = ('category', 'is_active')
    ordering = ('-created_at',)

admin.site.register(Resource, ResourceAdmin)
admin.site.register(ResourceCategory)
