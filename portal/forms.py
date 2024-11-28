# kcse_portal/forms.py
from django import forms
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from .models import (
    Student, StudentMarks, Subject, 
    School, County, ExaminationSession
)

class StudentRegistrationForm(forms.ModelForm):
    """Form for registering new students"""
    INDEX_NUMBER_VALIDATOR = RegexValidator(
        r'^\d{4}/\d{4}$', 
        message='Index number must be in format XXXX/XXXX (e.g., 2023/0001)'
    )

    index_number = forms.CharField(
        validators=[INDEX_NUMBER_VALIDATOR],
        help_text='Enter index number in format YYYY/NNNN'
    )

    class Meta:
        model = Student
        fields = [
            'first_name', 'last_name', 'index_number', 
            'gender', 'date_of_birth', 'school'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_index_number(self):
        """Ensure index number is unique"""
        index_number = self.cleaned_data['index_number']
        if Student.objects.filter(index_number=index_number).exists():
            raise ValidationError("This index number is already registered.")
        return index_number

class StudentMarkEntryForm(forms.ModelForm):
    """Form for entering student marks"""
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

    score = forms.IntegerField(
        validators=[
            MinValueValidator(0, message='Score cannot be negative'),
            MaxValueValidator(100, message='Score cannot exceed 100')
        ]
    )

    grade = forms.ChoiceField(choices=GRADE_CHOICES)

    class Meta:
        model = StudentMarks
        fields = [
            'student', 'subject', 'examination_session', 
            'score', 'grade'
        ]

    def clean(self):
        """Custom validation for mark entry"""
        cleaned_data = super().clean()
        student = cleaned_data.get('student')
        subject = cleaned_data.get('subject')
        examination_session = cleaned_data.get('examination_session')

        # Check for duplicate marks entry
        if StudentMarks.objects.filter(
            student=student, 
            subject=subject, 
            examination_session=examination_session
        ).exists():
            raise ValidationError("Marks for this student, subject, and session already exist.")

        return cleaned_data

class SchoolPerformanceFilterForm(forms.Form):
    """Form for filtering school performance"""
    county = forms.ModelChoiceField(
        queryset=County.objects.all(), 
        required=False,
        help_text='Select a county to filter results'
    )

    school = forms.ModelChoiceField(
        queryset=School.objects.all(), 
        required=False,
        help_text='Select a specific school'
    )

    examination_session = forms.ModelChoiceField(
        queryset=ExaminationSession.objects.all(), 
        required=False,
        help_text='Select an examination session'
    )

class SubjectRegistrationForm(forms.ModelForm):
    """Form for registering new subjects"""
    class Meta:
        model = Subject
        fields = ['name', 'code', 'category']
        
    def clean_code(self):
        """Ensure subject code is unique"""
        code = self.cleaned_data['code']
        if Subject.objects.filter(code=code).exists():
            raise ValidationError("A subject with this code already exists.")
        return code

class SchoolRegistrationForm(forms.ModelForm):
    """Form for registering new schools"""
    SCHOOL_TYPE_CHOICES = [
        ('PUBLIC', 'Public School'),
        ('PRIVATE', 'Private School'),
        ('NATIONAL', 'National School'),
        ('COUNTY', 'County School')
    ]

    school_type = forms.ChoiceField(choices=SCHOOL_TYPE_CHOICES)

    class Meta:
        model = School
        fields = ['name', 'school_code', 'county', 'address', 'school_type']

    def clean_school_code(self):
        """Ensure school code is unique"""
        school_code = self.cleaned_data['school_code']
        if School.objects.filter(school_code=school_code).exists():
            raise ValidationError("A school with this code already exists.")
        return school_code

class ExaminationSessionForm(forms.ModelForm):
    """Form for creating examination sessions"""
    class Meta:
        model = ExaminationSession
        fields = ['year', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        """Validate date range"""
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise ValidationError("Start date must be before end date.")

        # Check for overlapping examination sessions
        if ExaminationSession.objects.filter(
            start_date__lte=end_date,
            end_date__gte=start_date
        ).exists():
            raise ValidationError("An examination session already exists for this period.")

        return cleaned_data

class DataExportForm(forms.Form):
    """Form for selecting export options"""
    EXPORT_CHOICES = [
        ('students', 'Student Data'),
        ('marks', 'Student Marks'),
        ('performance', 'Performance Data'),
        ('school', 'School Data')
    ]

    export_type = forms.ChoiceField(
        choices=EXPORT_CHOICES,
        widget=forms.Select,
        help_text='Select the type of data to export'
    )

    file_format = forms.ChoiceField(
        choices=[
            ('xlsx', 'Excel (.xlsx)'),
            ('csv', 'CSV (.csv)'),
            ('json', 'JSON (.json)')
        ],
        initial='xlsx',
        help_text='Choose the file format for export'
    )