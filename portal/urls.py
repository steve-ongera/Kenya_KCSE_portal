# kcse_portal/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication Routes
    path('login/', auth_views.LoginView.as_view(template_name='kcse_portal/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # Dashboard and Home Routes
    path('', views.dashboard, name='dashboard'),
    
    # Student-related Routes
    path('students/', views.student_performance_list, name='student_list'),
    path('students/register/', views.student_registration, name='student_registration'),
    path('students/<int:student_id>/', views.student_detail, name='student_detail'),
    
    # Marks and Performance Routes
    path('marks/entry/', views.mark_entry, name='mark_entry'),
    path('performance/students/', views.student_performance_list, name='student_performance'),
    path('performance/schools/', views.school_performance, name='school_performance'),
    path('performance/subjects/', views.subject_performance, name='subject_performance'),
    path('performance/counties/', views.county_performance, name='county_performance'),
    
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
