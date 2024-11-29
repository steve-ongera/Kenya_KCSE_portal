
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

