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
