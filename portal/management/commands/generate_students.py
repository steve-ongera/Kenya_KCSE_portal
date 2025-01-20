import random
from datetime import date
from portal.models import Student, School

def generate_students_2023():
    # Fetch all schools
    schools = list(School.objects.all())
    
    if not schools:
        print("No schools available in the database. Please add some schools first.")
        return
    
    # Kenyan names for student generation
    first_names = [
        "Achieng", "Atieno", "Kamau", "Wanjiku", "Njeri", "Omondi", 
        "Okoth", "Chebet", "Cheruiyot", "Mutua", "Otieno", "Mwende", 
        "Wafula", "Muthoni", "Anyango", "Kiprotich", "Njenga", "Karanja", 
        "Makena", "Kiplagat", "Wambui", "Ngugi", "Maina", "Kilonzo"
    ]
    last_names = [
        "Omondi", "Odhiambo", "Mwangi", "Mutiso", "Kiprotich", "Cheruiyot", 
        "Kibaki", "Owino", "Mugendi", "Kamau", "Okello", "Chepkemoi", 
        "Mutua", "Wambua", "Njuguna", "Mwaniki", "Ndung'u", "Wanyama", 
        "Otieno", "Ruto", "Obuya", "Onyango", "Ng'etich", "Koech"
    ]
    genders = ["M", "F"]
    
    # Dictionary to track index numbers for each school
    school_counts = {school.school_code: 1 for school in schools}
    
    # Generate 1700 students
    for _ in range(1700):
        school = random.choice(schools)
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        gender = random.choice(genders)
        date_of_birth = date(2005, random.randint(1, 12), random.randint(1, 28))  # Birth year for 2023 candidates
        
        # Generate unique index number
        index_number = f"{school.school_code}/{school_counts[school.school_code]:04d}/2023"
        school_counts[school.school_code] += 1
        
        student = Student(
            first_name=first_name,
            last_name=last_name,
            index_number=index_number,
            gender=gender,
            date_of_birth=date_of_birth,
            school=school,
            year=2023
        )
        try:
            student.save()
            print(f"Created student: {student}")
        except Exception as e:
            print(f"Failed to create student {first_name} {last_name}: {e}")

# Run the function
generate_students_2023()
