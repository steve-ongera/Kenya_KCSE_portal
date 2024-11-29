
def calculate_grade(mean_score):
    """Determine grade based on mean score."""
    if mean_score >= 80:
        return 'A'
    elif mean_score >= 75:
        return 'A-'
    elif mean_score >= 70:
        return 'B+'
    elif mean_score >= 65:
        return 'B'
    elif mean_score >= 60:
        return 'B-'
    elif mean_score >= 55:
        return 'C+'
    elif mean_score >= 50:
        return 'C'
    elif mean_score >= 45:
        return 'C-'
    elif mean_score >= 40:
        return 'D+'
    elif mean_score >= 35:
        return 'D'
    elif mean_score >= 30:
        return 'D-'
    else:
        return 'E'

def calculate_points(mean_score):
    """Determine points based on mean score."""
    if mean_score >= 80:
        return 12
    elif mean_score >= 75:
        return 11
    elif mean_score >= 70:
        return 10
    elif mean_score >= 65:
        return 9
    elif mean_score >= 60:
        return 8
    elif mean_score >= 55:
        return 7
    elif mean_score >= 50:
        return 6
    elif mean_score >= 45:
        return 5
    elif mean_score >= 40:
        return 4
    elif mean_score >= 35:
        return 3
    elif mean_score >= 30:
        return 2
    else:
        return 1


# utils.py

def calculate_grade_from_points(points):
    """Determine grade based on points (with decimal handling)."""
    if points >= 11:
        return 'A'  # 11 and 12 points -> A
    elif points >= 10:
        return 'A-'
    elif points >= 9:
        return 'B+'
    elif points >= 8:
        return 'B'
    elif points >= 7:
        return 'B-'
    elif points >= 6:  # Handles all points in the range [6, 6.9]
        return 'C+'
    elif points >= 5:
        return 'C'
    elif points >= 4:
        return 'C-'
    elif points >= 3:
        return 'D+'
    elif points >= 2:
        return 'D'
    elif points >= 1:
        return 'D-'
    else:
        return 'E'


def compute_school_statistics(school):
    """Compute mean points, mean grade, and students who will join university (C+ and above)."""
    # Calculate the mean points of all students in the school
    students = school.students.all()
    total_points = 0
    students_above_c_plus = 0

    for student in students:
        try:
            # Get the student's overall performance for the latest session
            overall_performance = student.overall_performances.latest('examination_session__year')
            total_points += overall_performance.total_points

            # Check if the student has C+ or above (points-based grade)
            if overall_performance.total_points >= 7:  # C+ or above
                students_above_c_plus += 1
        except student.overall_performances.model.DoesNotExist:
            continue  # If no performance found for the student, ignore and continue

    # Calculate the mean points
    mean_points = total_points / len(students) if len(students) > 0 else 0
    # Calculate the mean grade based on the points (from our updated scale)
    mean_grade = calculate_grade_from_points(mean_points)

    return mean_points, mean_grade, students_above_c_plus
