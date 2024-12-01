# kcse_portal/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication Routes
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.custom_logout, name='logout'),
    path('help-and-support/', views.help_and_support, name='help_and_support'),
    path('system-settings/', views.system_settings, name='system_settings'),
    
    # Dashboard and Home Routes
    path('', views.dashboard, name='dashboard'),
    
    # Student-related Routes
    path('student_performance_list/', views.student_performance_list, name='student_performance_list'),
    path('students/register/', views.student_registration, name='student_registration'),
    path('students/<int:student_id>/', views.student_detail, name='student_detail'),
    path('students_list/', views.student_list, name='student_list'),  # List all students
    path('students/add/', views.add_student, name='add_student'),  # Add a student
    path('students/<int:student_id>/edit/', views.update_student, name='update_student'),  # Update student
    path('students/<int:student_id>/delete/', views.delete_student, name='delete_student'),  # Delete student

    
    # Marks and Performance Routes
    path('marks/entry/', views.mark_entry, name='mark_entry'),
    path('performance/students/', views.student_performance_list, name='student_performance'),# no need of this
    path('performance/schools/', views.school_performance, name='school_performance'),
    path('performance/subjects/', views.subject_performance, name='subject_performance'),
    path('performance/counties/', views.county_performance, name='county_performance'),
    
    #subject views 
    path('subjects/', views.subject_list, name='subject_list'),  # List all subjects
    path('subjects/add/', views.add_subject, name='add_subject'),  # Add a subject
    path('subjects/<int:subject_id>/edit/', views.update_subject, name='update_subject'),  # Update subject
    path('subjects/<int:subject_id>/delete/', views.delete_subject, name='delete_subject'),  # Delete subject
     
     #examination_session 
    path('examination_sessions/', views.examination_session_list, name='examination_session_list'),  # List all sessions
    path('examination_sessions/add/', views.add_examination_session, name='add_examination_session'),  # Add a session
    path('examination_sessions/<int:session_id>/edit/', views.update_examination_session, name='update_examination_session'),  # Edit session
    path('examination_sessions/<int:session_id>/delete/', views.delete_examination_session, name='delete_examination_session'),  # Delete session
    
    #marks entry
    path('student_marks/', views.student_marks_list, name='student_marks_list'),  # List all marks
    path('student_marks/add/', views.add_student_marks, name='add_student_marks'),  # Add new marks
    path('student_marks/<int:marks_id>/edit/', views.update_student_marks, name='update_student_marks'),  # Edit marks
    path('student_marks/<int:marks_id>/delete/', views.delete_student_marks, name='delete_student_marks'),  # Delete marks
    
    #overall performance 
    path('student_overall_performance/', views.student_overall_performance_list, name='student_overall_performance_list'),  # List all performances
    path('student_overall_performance/add/', views.add_student_overall_performance, name='add_student_overall_performance'),  # Add new performance
    path('student_overall_performance/<int:performance_id>/edit/', views.update_student_overall_performance, name='update_student_overall_performance'),  # Edit performance
    path('student_overall_performance/<int:performance_id>/delete/', views.delete_student_overall_performance, name='delete_student_overall_performance'),  # Delete performance

    #search student results
    path('student_marks/search/', views.search_student_marks, name='search_student_marks'),
    #school list view
    path('schools/', views.all_schools_view, name='all_schools'),
    path('school/<int:school_id>/', views.school_details_view, name='school_details'),

    #ranking
    path('top-students/', views.top_students, name='top_students'),
    path('top-100-schools/', views.top_100_schools, name='top_100_schools'),
    path('students-above-c-plus/<int:school_id>/', views.students_above_c_plus, name='students_above_c_plus'),
    path('subject-ranking/', views.rank_subjects, name='subject_ranking'),
    #exam centers
    path('exam-centers/', views.list_exam_centers, name='list_exam_centers'),
    path('exam-centers/create/', views.create_exam_center, name='create_exam_center'),
    path('exam-centers/update/<int:pk>/', views.update_exam_center, name='update_exam_center'),
    path('exam-centers/delete/<int:pk>/', views.delete_exam_center, name='delete_exam_center'),
    #timetable
    path('timetable/', views.timetable_list, name='timetable_list'),
    path('timetable/create/', views.create_timetable, name='create_timetable'),
    path('timetable/update/<int:pk>/', views.update_timetable, name='update_timetable'),
    path('timetable/delete/<int:pk>/', views.delete_timetable, name='delete_timetable'),
    path('exam-timetable/<int:pk>/', views.exam_timetable_detail, name='exam_timetable_detail'),
    #resources views
    path('resources/add/', views.add_resource, name='add_resource'),
    path('resources/', views.resources_list, name='resources_list'),
    path('resources/<int:resource_id>/', views.resource_detail, name='resource_detail'),
    path('resource-search/', views.resource_search, name='resource_search'),
    
    # Export Routes
    path('export/', views.data_export, name='data_export'),
    
    # Password Management Routes
    path('password_change/', 
         auth_views.PasswordChangeView.as_view(template_name='kcse_portal/password_change.html'), 
         name='password_change'),
    path('password_change/done/', 
         auth_views.PasswordChangeDoneView.as_view(template_name='kcse_portal/password_change_done.html'), 
         name='password_change_done'),
    
    # Password Reset Routes
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(template_name='kcse_portal/password_reset.html'), 
         name='password_reset'),
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='kcse_portal/password_reset_done.html'), 
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='kcse_portal/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='kcse_portal/password_reset_complete.html'), 
         name='password_reset_complete'),
]
