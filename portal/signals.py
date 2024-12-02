from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import StudentMarks, StudentOverallPerformance
from .models import calculate_grade, calculate_points

@receiver(post_save, sender=StudentMarks)
def update_student_overall_performance(sender, instance, **kwargs):
    """Automatically calculate and update overall performance."""
    student = instance.student
    session = instance.examination_session

    # Retrieve all marks for the student in the same session
    marks = StudentMarks.objects.filter(student=student, examination_session=session)

    # Calculate total score and mean score
    total_score = sum(mark.score for mark in marks)
    subject_count = marks.count()
    mean_score = total_score / subject_count if subject_count else 0

    # Calculate grade and points
    mean_grade = calculate_grade(mean_score)
    total_points = calculate_points(mean_score)

    # Update or create the StudentOverallPerformance entry
    StudentOverallPerformance.objects.update_or_create(
        student=student,
        examination_session=session,
        defaults={
            'total_score': total_score,
            'mean_grade': mean_grade,
            'total_points': total_points
        }
    )


from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import Activity

@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    Activity.objects.create(
        user=user,
        action="Logged in",
        ip_address=get_client_ip(request),
    )

@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    Activity.objects.create(
        user=user,
        action="Logged out",
        ip_address=get_client_ip(request),
    )

def get_client_ip(request):
    """Helper function to get the client's IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Profile, Activity

@receiver(post_save, sender=Profile)
def track_profile_save(sender, instance, created, **kwargs):
    if created:
        action = f"Created profile for {instance.full_names} (Role: {instance.role})"
    else:
        action = f"Updated profile for {instance.full_names} (Role: {instance.role})"
    Activity.objects.create(
        user=instance.user,
        action=action
    )

@receiver(post_delete, sender=Profile)
def track_profile_delete(sender, instance, **kwargs):
    action = f"Deleted profile for {instance.full_names} (Role: {instance.role})"
    Activity.objects.create(
        user=instance.user,
        action=action
    )
