# kcse_portal/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Avg, Sum, Count, Q
from django.http import HttpResponse, JsonResponse
from django.db.models import F
import pandas as pd
import io

from .models import (
    County, School, Student, Subject, 
    ExaminationSession, StudentMarks, 
    StudentOverallPerformance
)
from .forms import (
    StudentMarkEntryForm, 
    StudentRegistrationForm, 
    SchoolPerformanceFilterForm
)

@login_required
def dashboard(request):
    """Main dashboard view for overview of KCSE performance"""
    # Total counts
    total_students = Student.objects.count()
    total_schools = School.objects.count()
    total_counties = County.objects.count()
    
    # Latest examination session
    try:
        latest_session = ExaminationSession.objects.latest('year')
        
        # Performance metrics
        national_performance = StudentOverallPerformance.objects.filter(
            examination_session=latest_session
        ).aggregate(
            mean_points=Avg('total_points'),
            total_students=Count('student')
        )
        
        # Top 5 performing counties
        top_counties = County.objects.annotate(
            avg_points=Avg('schools__students__overallperformance__total_points')
        ).order_by('-avg_points')[:5]
        
        context = {
            'total_students': total_students,
            'total_schools': total_schools,
            'total_counties': total_counties,
            'national_performance': national_performance,
            'top_counties': top_counties,
            'latest_session': latest_session
        }
    except ExaminationSession.DoesNotExist:
        context = {
            'total_students': total_students,
            'total_schools': total_schools,
            'total_counties': total_counties,
        }
    
    return render(request, 'kcse_portal/dashboard.html', context)

@login_required
def student_performance_list(request):
    """List and filter student performances"""
    # Initial queryset
    performances = StudentOverallPerformance.objects.select_related(
        'student', 'student__school', 'examination_session'
    )
    
    # Filter form
    filter_form = SchoolPerformanceFilterForm(request.GET)
    
    # Apply filters
    if filter_form.is_valid():
        if filter_form.cleaned_data.get('county'):
            performances = performances.filter(student__school__county=filter_form.cleaned_data['county'])
        
        if filter_form.cleaned_data.get('school'):
            performances = performances.filter(student__school=filter_form.cleaned_data['school'])
        
        if filter_form.cleaned_data.get('examination_session'):
            performances = performances.filter(examination_session=filter_form.cleaned_data['examination_session'])
    
    # Performance breakdown by grade
    performance_breakdown = performances.values('mean_grade').annotate(
        student_count=Count('id')
    ).order_by('mean_grade')
    
    context = {
        'performances': performances,
        'filter_form': filter_form,
        'performance_breakdown': performance_breakdown
    }
    
    return render(request, 'kcse_portal/student_performance_list.html', context)

@login_required
def student_detail(request, student_id):
    """Detailed view of a student's performance"""
    # Get student with related performance data
    student = get_object_or_404(Student, pk=student_id)
    
    # Student's overall performances
    performances = StudentOverallPerformance.objects.filter(student=student)
    
    # Detailed subject marks
    subject_marks = StudentMarks.objects.filter(student=student).select_related(
        'subject', 'examination_session'
    )
    
    context = {
        'student': student,
        'performances': performances,
        'subject_marks': subject_marks
    }
    
    return render(request, 'kcse_portal/student_detail.html', context)

@login_required
@permission_required('kcse_portal.add_studentmarks')
def mark_entry(request):
    """View for entering student marks"""
    if request.method == 'POST':
        form = StudentMarkEntryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('mark_entry_success')
    else:
        form = StudentMarkEntryForm()
    
    return render(request, 'kcse_portal/mark_entry.html', {'form': form})

@login_required
def school_performance(request):
    """School performance analysis"""
    # Get all schools with their performance metrics
    schools = School.objects.annotate(
        avg_points=Avg('students__overallperformance__total_points'),
        total_students=Count('students'),
        top_performers=Count('students__overallperformance', 
                             filter=Q(students__overallperformance__mean_grade__in=['A', 'A-']))
    ).order_by('-avg_points')
    
    # Group performance by county
    county_performance = County.objects.annotate(
        avg_county_points=Avg('schools__students__overallperformance__total_points'),
        total_schools=Count('schools')
    ).order_by('-avg_county_points')
    
    context = {
        'schools': schools,
        'county_performance': county_performance
    }
    
    return render(request, 'kcse_portal/school_performance.html', context)

@login_required
@permission_required('kcse_portal.export_data')
def data_export(request):
    """Export data to Excel"""
    export_type = request.GET.get('export_type', 'students')
    
    try:
        # Select appropriate data based on export type
        if export_type == 'students':
            queryset = Student.objects.select_related('school', 'school__county')
            data = list(queryset.values())
        elif export_type == 'marks':
            queryset = StudentMarks.objects.select_related('student', 'subject')
            data = list(queryset.values())
        elif export_type == 'performance':
            queryset = StudentOverallPerformance.objects.select_related('student', 'examination_session')
            data = list(queryset.values())
        else:
            return HttpResponse('Invalid export type', status=400)
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Create Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        
        output.seek(0)
        response = HttpResponse(
            output.read(), 
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename={export_type}_export.xlsx'
        
        return response
    
    except Exception as e:
        return HttpResponse(f'Export error: {str(e)}', status=500)

@login_required
def subject_performance(request):
    """Subject-wise performance analysis"""
    # Top performing subjects
    subjects = Subject.objects.annotate(
        avg_score=Avg('studentmarks__score'),
        total_students=Count('studentmarks__student', distinct=True)
    ).order_by('-avg_score')
    
    # Gender-based subject performance
    gender_performance = StudentMarks.objects.values(
        'subject__name', 'student__gender'
    ).annotate(
        avg_score=Avg('score'),
        student_count=Count('student', distinct=True)
    )
    
    context = {
        'subjects': subjects,
        'gender_performance': gender_performance
    }
    
    return render(request, 'kcse_portal/subject_performance.html', context)

@login_required
def student_registration(request):
    """Student registration view"""
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('student_registration_success')
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'kcse_portal/student_registration.html', {'form': form})

@login_required
def county_performance(request):
    """County-level performance analysis"""
    # Performance by county
    counties = County.objects.annotate(
        avg_points=Avg('schools__students__overallperformance__total_points'),
        total_students=Count('schools__students'),
        total_schools=Count('schools')
    ).order_by('-avg_points')
    
    context = {
        'counties': counties
    }
    
    return render(request, 'kcse_portal/county_performance.html', context)