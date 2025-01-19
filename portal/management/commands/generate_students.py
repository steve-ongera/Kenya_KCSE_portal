import random
from datetime import date
from portal.models import Student, School

def generate_students():
    # Fetch all schools
    schools = list(School.objects.all())
    
    if not schools:
        print("No schools available in the database. Please add some schools first.")
        return
    
    # Predefined data for student generation
    first_names = ["John", "Mary", "Alice", "James", "Jane", "Robert", "Emily", "Michael", "Sarah", "Daniel"]
    last_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor"]
    genders = ["M", "F"]
    
    # Generate 100 students
    for i in range(1, 101):
        school = random.choice(schools)
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        gender = random.choice(genders)
        date_of_birth = date(2007, random.randint(1, 12), random.randint(1, 28))  # Birth year for 2025 candidates
        
        index_number = f"{school.school_code}/{i:03d}/2025"
        
        student = Student(
            first_name=first_name,
            last_name=last_name,
            index_number=index_number,
            gender=gender,
            date_of_birth=date_of_birth,
            school=school,
            year=2025
        )
        student.save()
        print(f"Created student: {student}")

# Run the function
generate_students()
