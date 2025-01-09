from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# Base User model
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
        ('staff', 'Staff'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

# Admin Profile
class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    admin_code = models.CharField(max_length=50)

# Doctor Profile
class DoctorProfile(models.Model):
    user = models.OneToOneField(User, related_name="doctor", on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50)
    hospital_name = models.CharField(max_length=100)

# Patient Profile
class PatientProfile(models.Model):
    user = models.OneToOneField(User,related_name="patient", on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    medical_history = models.TextField(blank=True)
    insurance_number = models.CharField(max_length=50, blank=True)

# Staff Profile
class StaffProfile(models.Model):
    user = models.OneToOneField(User,related_name="staff", on_delete=models.CASCADE)
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, null=True, blank=True)
    department = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=50)





import uuid
def generate_appointment(*args,**kwargs):
    return (str(uuid.uuid4())).split('-')[0].upper()

class Appointment(models.Model):
    appointment_number = models.CharField(unique=True,max_length=100, default=generate_appointment)
    scheduled = models.DateTimeField()
    remarks = models.CharField(max_length=100)
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)

