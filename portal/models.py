# kcse_portal/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class County(models.Model):
    """Represents Kenyan Counties"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name

class School(models.Model):
    """Represents Secondary Schools in Kenya"""
    name = models.CharField(max_length=200)
    school_code = models.CharField(max_length=20, unique=True)
    county = models.ForeignKey(County, on_delete=models.CASCADE, related_name='schools')
    address = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} ({self.school_code})"

class Student(models.Model):
    """Represents a student in the KCSE examination"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female')
    ]
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    index_number = models.CharField(max_length=20, unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='students')
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.index_number})"

class Subject(models.Model):
    """Represents KCSE Subjects"""
    SUBJECT_CATEGORIES = [
        ('COMPULSORY', 'Compulsory'),
        ('OPTIONAL', 'Optional')
    ]
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    category = models.CharField(max_length=20, choices=SUBJECT_CATEGORIES)
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class ExaminationSession(models.Model):
    """Represents a specific KCSE Examination Session"""
    year = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    
    def __str__(self):
        return f"KCSE {self.year}"

class StudentMarks(models.Model):
    """Stores marks for individual students in specific subjects"""
    GRADE_CHOICES = [
        ('A', 'A Plain'),
        ('A-', 'A Minus'),
        ('B+', 'B Plus'),
        ('B', 'B Plain'),
        ('B-', 'B Minus'),
        ('C+', 'C Plus'),
        ('C', 'C Plain'),
        ('C-', 'C Minus'),
        ('D+', 'D Plus'),
        ('D', 'D Plain'),
        ('D-', 'D Minus'),
        ('E', 'E')
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='marks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    examination_session = models.ForeignKey(ExaminationSession, on_delete=models.CASCADE)
    score = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ]
    )
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES)
    
    class Meta:
        unique_together = ('student', 'subject', 'examination_session')
        verbose_name_plural = "Student Marks"
    
    def __str__(self):
        return f"{self.student.index_number} - {self.subject.name} - {self.grade}"

class StudentOverallPerformance(models.Model):
    """Captures overall performance of a student in a specific examination session"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    examination_session = models.ForeignKey(ExaminationSession, on_delete=models.CASCADE)
    total_score = models.IntegerField()
    mean_grade = models.CharField(max_length=2)
    total_points = models.FloatField()
    
    class Meta:
        unique_together = ('student', 'examination_session')
        verbose_name_plural = "Student Overall Performances"
    
    def __str__(self):
        return f"{self.student.index_number} - {self.examination_session.year} - {self.mean_grade}"
