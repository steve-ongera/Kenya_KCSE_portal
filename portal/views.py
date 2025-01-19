# kcse_portal/views.py
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Avg, Sum, Count, Q
from django.http import HttpResponse, JsonResponse
from django.db.models import F
import pandas as pd
import io
from collections import defaultdict
from django.urls import reverse

from .models import *

from .forms import *
from .utils import compute_school_statistics
from django.db.models import Avg
##new changes in dashboard 
from django.db.models import Count
from django.db.models.functions import ExtractYear

@login_required
def dashboard(request):
    # Fetch gender distribution by year
    students = Student.objects.values('year', 'gender').annotate(count=Count('id')).order_by('year')

    # Prepare the data for Chart.js
    gender_data = {
        'years': [],
        'male_counts': [],
        'female_counts': [],
        'total_counts': {}  # Store the total count for each year
    }

    # Populate the data
    for student in students:
        year = student['year']
        gender = student['gender']
        if gender == 'M':
            gender_data['male_counts'].append(student['count'])
        elif gender == 'F':
            gender_data['female_counts'].append(student['count'])
        
        if year not in gender_data['years']:
            gender_data['years'].append(year)

        # Store total number of students for each year (male + female)
        if year not in gender_data['total_counts']:
            gender_data['total_counts'][year] = 0
        
        gender_data['total_counts'][year] += student['count']

    
    
    # Get the top 6 students sorted by total score in descending order
    top_students = StudentOverallPerformance.objects.all().order_by('-total_score')[:14]

    # Add school information to each student's performance
    students_with_school = []
    for performance in top_students:
        student = performance.student
        school = student.school  # Assuming the Student model has a foreign key to the School model
        students_with_school.append({
            'student': student,
            'performance': performance,
            'school': school
        })

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
            avg_points=Avg('schools__students__overall_performances__total_points')
        ).order_by('-avg_points')[:5]

        recent_activities = Activity.objects.order_by('-timestamp')[:5]
        
        context = {
            'total_students': total_students,
            'total_schools': total_schools,
            'total_counties': total_counties,
            'national_performance': national_performance,
            'top_counties': top_counties,
            'latest_session': latest_session,
            'recent_activities': recent_activities,
            'students_with_school':students_with_school,
            'years': gender_data['years'],
            'male_counts': gender_data['male_counts'],
            'female_counts': gender_data['female_counts'],
            'total_counts': gender_data['total_counts']
        }
    except ExaminationSession.DoesNotExist:
        context = {
            'students_with_school':students_with_school,
            'total_students': total_students,
            'total_schools': total_schools,
            'total_counties': total_counties,
            'recent_activities': Activity.objects.order_by('-timestamp')[:5],  # Ensure this is always available
            
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


# Create view: Add a new student
def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('student_list')  # Redirect to the student list view
    else:
        form = StudentForm()
    return render(request, 'portal/add_student.html', {'form': form})

# Read view: List all students
def student_list(request):
    students = Student.objects.all()
    return render(request, 'portal/student_list.html', {'students': students})

# Update view: Edit a student's details
def update_student(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_list')
    else:
        form = StudentForm(instance=student)
    return render(request, 'portal/update_student.html', {'form': form , 'student': student})

# Delete view: Delete a student
def delete_student(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    if request.method == 'POST':
        student.delete()
        return redirect('student_list')
    return render(request, 'portal/delete_student.html', {'student': student})



# Create view: Add a new subject
def add_subject(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('subject_list')  # Redirect to the subject list view
    else:
        form = SubjectForm()
    return render(request, 'subject/add_subject.html', {'form': form})

# Read view: List all subjects
def subject_list(request):
    subjects = Subject.objects.all()
    return render(request, 'subject/subject_list.html', {'subjects': subjects})

# Update view: Edit an existing subject
def update_subject(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            return redirect('subject_list')
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'subject/update_subject.html', {'form': form})

# Delete view: Delete a subject
def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    if request.method == 'POST':
        subject.delete()
        return redirect('subject_list')
    return render(request, 'subject/delete_subject.html', {'subject': subject})


# Create view: Add a new examination session
def add_examination_session(request):
    if request.method == 'POST':
        form = ExaminationSessionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('examination_session_list')  # Redirect to the session list view
    else:
        form = ExaminationSessionForm()
    return render(request, 'examination_session/add_examination_session.html', {'form': form})

# Read view: List all examination sessions
def examination_session_list(request):
    sessions = ExaminationSession.objects.all()
    return render(request, 'examination_session/examination_session_list.html', {'sessions': sessions})

# Update view: Edit an existing examination session
def update_examination_session(request, session_id):
    session = get_object_or_404(ExaminationSession, pk=session_id)
    if request.method == 'POST':
        form = ExaminationSessionForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
            return redirect('examination_session_list')
    else:
        form = ExaminationSessionForm(instance=session)
    return render(request, 'examination_session/update_examination_session.html', {'form': form})

# Delete view: Delete an examination session
def delete_examination_session(request, session_id):
    session = get_object_or_404(ExaminationSession, pk=session_id)
    if request.method == 'POST':
        session.delete()
        return redirect('examination_session_list')
    return render(request, 'examination_session/delete_examination_session.html', {'session': session})


# Create view: Add a new student marks record
def add_student_marks(request):
    if request.method == 'POST':
        form = StudentMarksForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('student_marks_list')  # Redirect to the student marks list view
    else:
        form = StudentMarksForm()
    return render(request, 'student_marks/add_student_marks.html', {'form': form})


# Read view: List all student marks
def student_marks_list(request):
    # Get all marks for the student
    student_marks = StudentMarks.objects.all()
    students = Student.objects.all()  # Get all students
    subjects = Subject.objects.all()  # Get all subjects

    # Create a dictionary to organize marks per student
    marks_dict = {}

    for student in students:
        student_marks_for_student = student_marks.filter(student=student)  # Get marks for the student
        marks_for_subjects = {}

        for mark in student_marks_for_student:
            marks_for_subjects[mark.subject.name] = mark  # Store marks with subject name as key

        marks_dict[student] = marks_for_subjects

    return render(request, 'student_marks/student_marks_list.html', {'students_marks': marks_dict, 'subjects': subjects})


# Update view: Edit an existing student marks record
def update_student_marks(request, marks_id):
    marks = get_object_or_404(StudentMarks, pk=marks_id)
    if request.method == 'POST':
        form = StudentMarksForm(request.POST, instance=marks)
        if form.is_valid():
            form.save()
            return redirect('student_marks_list')
    else:


        form = StudentMarksForm(instance=marks)
    return render(request, 'student_marks/update_student_marks.html', {'form': form})


# Delete view: Delete a student marks record
def delete_student_marks(request, marks_id):
    marks = get_object_or_404(StudentMarks, pk=marks_id)
    if request.method == 'POST':
        marks.delete()
        return redirect('student_marks_list')
    return render(request, 'student_marks/delete_student_marks.html', {'marks': marks})



# Create view: Add a new student overall performance record
def add_student_overall_performance(request):
    if request.method == 'POST':
        form = StudentOverallPerformanceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('student_overall_performance_list')  # Redirect to the list view
    else:
        form = StudentOverallPerformanceForm()
    return render(request, 'student_overall_performance/add_student_overall_performance.html', {'form': form})

# Read view: List all student overall performances
def student_overall_performance_list(request):
    performances = StudentOverallPerformance.objects.all()
    return render(request, 'student_overall_performance/student_overall_performance_list.html', {'performances': performances})

# Update view: Edit an existing student overall performance record
def update_student_overall_performance(request, performance_id):
    performance = get_object_or_404(StudentOverallPerformance, pk=performance_id)
    if request.method == 'POST':
        form = StudentOverallPerformanceForm(request.POST, instance=performance)
        if form.is_valid():
            form.save()
            return redirect('student_overall_performance_list')
    else:
        form = StudentOverallPerformanceForm(instance=performance)
    return render(request, 'student_overall_performance/update_student_overall_performance.html', {'form': form})

# Delete view: Delete a student overall performance record
def delete_student_overall_performance(request, performance_id):
    performance = get_object_or_404(StudentOverallPerformance, pk=performance_id)
    if request.method == 'POST':
        performance.delete()
        return redirect('student_overall_performance_list')
    return render(request, 'student_overall_performance/delete_student_overall_performance.html', {'performance': performance})


#search for student result

def search_student_marks(request):
    student = None
    marks = []
    examination_session = None
    overall_performance = None
    search_name = request.GET.get('name', '').strip()
    search_index = request.GET.get('index_number', '').strip()

    if search_name and search_index:
        try:
            # Retrieve the student if both name and index number match
            student = Student.objects.get(
                index_number=search_index,
                first_name__icontains=search_name.split()[0],  # Match first name
                last_name__icontains=search_name.split()[-1]   # Match last name
            )
            # Fetch marks for the student
            marks = StudentMarks.objects.filter(student=student).select_related('subject', 'examination_session')

            # Get the examination session from the first mark
            if marks.exists():
                examination_session = marks.first().examination_session

                # Fetch overall performance for the student in the session
                overall_performance = StudentOverallPerformance.objects.filter(
                    student=student,
                    examination_session=examination_session
                ).first()

        except Student.DoesNotExist:
            student = None

    return render(
        request,
        'kcse_portal/search_student_marks.html',
        {
            'student': student,
            'marks': marks,
            'search_name': search_name,
            'search_index': search_index,
            'examination_session': examination_session,
            'overall_performance': overall_performance,
        }
    )

#school list views
def all_schools_view(request):
    # Fetch all schools from the database
    schools = School.objects.all()
    
    return render(
        request,
        'school/all_schools.html',
        {'schools': schools}
    )


def school_details_view(request, school_id):
    # Retrieve the school based on the ID
    school = get_object_or_404(School, id=school_id)
    
    # Retrieve all students in the school
    students = Student.objects.filter(school=school)
    
    student_performance = []

    # Get performance data for each student
    for student in students:
        # Retrieve the overall performance for the student
        performance = StudentOverallPerformance.objects.filter(student=student).first()  # Assuming the most recent record is required

        if performance:
            student_performance.append({
                'student': student,
                'total_score': performance.total_score,
                'total_points': performance.total_points,
                'mean_grade': performance.mean_grade,
                'registration_number': student.index_number,  # Assuming registration_number is the student's index number
                'examination_session': performance.examination_session
            })
    
    return render(
        request,
        'school/school_details.html',  # Adjust to the correct template path
        {'school': school, 'student_performance': student_performance}
    )


def top_students(request):
    # Get the top 50 students sorted by total score in descending order
    top_students = StudentOverallPerformance.objects.all().order_by('-total_score')[:50]

    # Add school information to each student's performance
    students_with_school = []
    for performance in top_students:
        student = performance.student
        school = student.school  # Assuming the Student model has a foreign key to the School model
        students_with_school.append({
            'student': student,
            'performance': performance,
            'school': school
        })
    
    return render(
        request,
        'ranking/top_students.html',
        {'students_with_school': students_with_school}
    )


def top_100_schools(request):
    # Get the latest examination session
    latest_session = ExaminationSession.objects.latest('year')

    # Define the threshold grades for above C+
    high_grades = ['A', 'A-', 'B+', 'B', 'C+']

    schools = School.objects.all()
    schools_data = []

    # Compute statistics for each school
    for school in schools:
        # Count students above C+ using StudentOverallPerformance
        students_above_c_plus = StudentOverallPerformance.objects.filter(
            student__school=school,
            examination_session=latest_session,
            mean_grade__in=high_grades
        ).count()

        # Get the count of students in the school
        student_count = school.students.count()

        # Rest of the view remains the same
        mean_points, mean_grade, _ = compute_school_statistics(school)

        schools_data.append({
            'school': school,
            'mean_points': mean_points,
            'mean_grade': mean_grade,
            'students_above_c_plus': students_above_c_plus,
            'student_count': student_count,
        })

    # Sort by mean_points in descending order to get the top 100
    schools_data = sorted(schools_data, key=lambda x: x['mean_points'], reverse=True)[:100]

    return render(request, 'ranking/top_100_schools.html', {'schools_data': schools_data})


def students_above_c_plus(request, school_id):
    try:
        # Get the specific school
        school = School.objects.get(id=school_id)

        # Get the latest examination session
        latest_session = ExaminationSession.objects.latest('year')

        # Define the threshold grades for above C+
        high_grades = ['A', 'A-', 'B+', 'B', 'C+']

        # Fetch students with overall performance above C+
        students_above_c_plus = StudentOverallPerformance.objects.filter(
            student__school=school,
            examination_session=latest_session,
            mean_grade__in=high_grades
        ).select_related('student')

        return render(request, 'ranking/students_above_c_plus.html', {
            'students': students_above_c_plus,
            'school': school,
            'examination_session': latest_session
        })
    except School.DoesNotExist:
        return render(request, 'error.html', {'message': 'School not found'})
    except ExaminationSession.DoesNotExist:
        return render(request, 'error.html', {'message': 'No examination session found'})


def rank_subjects(request):
    # Get the latest examination session
    latest_session = ExaminationSession.objects.latest('year')

    # Fetch all subjects
    subjects = Subject.objects.all()
    subjects_data = []

    for subject in subjects:
        # Get marks for this subject in the latest session
        subject_marks = StudentMarks.objects.filter(
            subject=subject, 
            examination_session=latest_session
        )

        # Calculate mean points for the subject
        mean_points = subject_marks.aggregate(
            avg_points=Avg('score')
        )['avg_points'] or 0

        # Convert mean points to grade
        if mean_points >= 80:
            mean_grade = 'A'
        elif mean_points >= 75:
            mean_grade = 'A-'
        elif mean_points >= 70:
            mean_grade = 'B+'
        elif mean_points >= 65:
            mean_grade = 'B'
        elif mean_points >= 60:
            mean_grade = 'B-'
        elif mean_points >= 55:
            mean_grade = 'C+'
        elif mean_points >= 50:
            mean_grade = 'C'
        elif mean_points >= 45:
            mean_grade = 'C-'
        elif mean_points >= 40:
            mean_grade = 'D+'
        elif mean_points >= 35:
            mean_grade = 'D'
        elif mean_points >= 30:
            mean_grade = 'D-'
        else:
            mean_grade = 'E'

        # Total students who attempted the subject
        total_students = subject_marks.count()

        subjects_data.append({
            'subject': subject,
            'mean_points': round(mean_points, 2),
            'mean_grade': mean_grade,
            'total_students': total_students,
        })

    # Sort subjects by mean points in descending orders
    subjects_data = sorted(subjects_data, key=lambda x: x['mean_points'], reverse=True)

    return render(request, 'ranking/subject_ranking.html', {'subjects_data': subjects_data})


#auth

# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            return redirect('dashboard')  # Redirect to your dashboard or home page
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'registration/login.html')

# Register view
def register_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            messages.success(request, "Your account has been created successfully!")
            return redirect("login")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()
    
    return render(request, "registration/register.html", {"form": form})



def custom_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')


# Create exam cenetr views
def create_exam_center(request):
    if request.method == "POST":
        form = ExamCenterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_exam_centers')
    else:
        form = ExamCenterForm()
    return render(request, 'exam_centers/create.html', {'form': form})

# Read
def list_exam_centers(request):
    centers = ExamCenter.objects.all()
    return render(request, 'exam_centers/list.html', {'centers': centers})

# Update
def update_exam_center(request, pk):
    center = get_object_or_404(ExamCenter, pk=pk)
    if request.method == "POST":
        form = ExamCenterForm(request.POST, instance=center)
        if form.is_valid():
            form.save()
            return redirect('list_exam_centers')
    else:
        form = ExamCenterForm(instance=center)
    return render(request, 'exam_centers/update.html', {'form': form})

# Delete
def delete_exam_center(request, pk):
    center = get_object_or_404(ExamCenter, pk=pk)
    if request.method == "POST":
        center.delete()
        return redirect('list_exam_centers')
    return render(request, 'exam_centers/delete.html', {'center': center})

#time table views

def timetable_list(request):
    timetables = ExamTimeTable.objects.select_related('session').all()
    return render(request, 'time_table/timetable_list.html', {'timetables': timetables})

def create_timetable(request):
    if request.method == 'POST':
        form = ExamTimeTableForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exam timetable created successfully.')
            return redirect('timetable_list')
    else:
        form = ExamTimeTableForm()
    return render(request, 'time_table/timetable_form.html', {'form': form})

def update_timetable(request, pk):
    timetable = get_object_or_404(ExamTimeTable, pk=pk)
    if request.method == 'POST':
        form = ExamTimeTableForm(request.POST, request.FILES, instance=timetable)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exam timetable updated successfully.')
            return redirect('timetable_list')
    else:
        form = ExamTimeTableForm(instance=timetable)
    return render(request, 'time_table/timetable_form.html', {'form': form})

def delete_timetable(request, pk):
    timetable = get_object_or_404(ExamTimeTable, pk=pk)
    timetable.delete()
    messages.success(request, 'Exam timetable deleted successfully.')
    return redirect('timetable_list')


def exam_timetable_detail(request, pk):
    # Get the ExamTimeTable object by its primary key (pk)
    timetable = get_object_or_404(ExamTimeTable, pk=pk)
    
    # Return the rendered template with the timetable object
    return render(request, 'time_table/exam_timetable_detail.html', {'timetable': timetable})


# View to display the help and support page
def help_and_support(request):
    return render(request, 'help/help_and_support.html')


# View to display the system settings page
def system_settings(request):
    return render(request, 'help/system_settings.html')

#resources views
def add_resource(request):
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Resource added successfully!")
            return redirect('resources_list')  # Redirect to the resource list page
        else:
            messages.error(request, "Error adding resource. Please try again.")
    else:
        form = ResourceForm()

    return render(request, 'resources/add_resource.html', {'form': form})


def resources_list(request):
    resources = Resource.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'resources/resources_list.html', {'resources': resources})

def resource_detail(request, resource_id):
    resource = Resource.objects.get(id=resource_id)
    resource.increment_views()  # Increment views count each time a resource is accessed
    return render(request, 'resources/resource_detail.html', {'resource': resource})


def resource_search(request):
    query = request.GET.get('query', '')
    resources = Resource.objects.filter(title__icontains=query)

    results = []

    for resource in resources:
        # Truncate description to 20 words (you can adjust this number)
        truncated_description = strip_tags(resource.description)  # Remove any HTML tags
        words = truncated_description.split()
        if len(words) > 20:
            truncated_description = ' '.join(words[:20]) + '...'  # Add three dots if the description is too long

        results.append({
            'title': resource.title,
            'description': truncated_description,
            'url': reverse('resource_detail', args=[resource.id]),
        })

    return JsonResponse({'resources': results})


@login_required
def profile_detail(request):
    try:
        # Get or create the user's profile
        profile, created = Profile.objects.get_or_create(user=request.user)
    except Profile.DoesNotExist:
        profile = None

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()  # Save the form with the new image
            return redirect('profile_detail')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'registration/profile_detail.html', {
        'profile': profile,
        'form': form,
    })


@login_required
def create_profile(request):
    # Check if the logged-in user already has a profile
    if hasattr(request.user, 'profile'):
        return redirect('profile_detail')  # If the user already has a profile, redirect to profile detail

    # Handle the form submission
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user  # Associate the profile with the logged-in user
            profile.save()
            return redirect('profile_detail')  # Redirect to profile detail after saving

    else:
        form = ProfileForm()

    return render(request, 'registration/create_profile.html', {'form': form})
