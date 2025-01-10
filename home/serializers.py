from django.contrib.auth import authenticate
from rest_framework import serializers, viewsets, status
from rest_framework.decorators import action
from .models import (
    User, AdminProfile, DoctorProfile, PatientProfile, StaffProfile,Appointment)

from django.contrib.auth.models import Permission

# Serializer for User Registration with Role-Specific Validation
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)
    admin_code = serializers.CharField(required=False, allow_blank=True)
    specialization = serializers.CharField(required=False, allow_blank=True)
    license_number = serializers.CharField(required=False, allow_blank=True)
    hospital_name = serializers.CharField(required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False)
    medical_history = serializers.CharField(required=False, allow_blank=True)
    insurance_number = serializers.CharField(required=False, allow_blank=True)
    department = serializers.CharField(required=False, allow_blank=True)
    employee_id = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'role', 'admin_code', 'specialization', 'license_number', 'hospital_name', 'date_of_birth', 'medical_history', 'insurance_number', 'department', 'employee_id']

    def validate(self, data):
        role = data.get('role')
        if role == 'admin' and not data.get('admin_code'):
            raise serializers.ValidationError({'admin_code': 'Admin code is required for admin role.'})
        if role == 'doctor' and not all([data.get('specialization'), data.get('license_number'), data.get('hospital_name')]):
            raise serializers.ValidationError('Specialization, license number, and hospital name are required for doctors.')
        if role == 'patient' and not data.get('date_of_birth'):
            raise serializers.ValidationError({'date_of_birth': 'Date of birth is required for patients.'})
        if role == 'staff' and not all([data.get('department'), data.get('employee_id')]):
            raise serializers.ValidationError('Department and employee ID are required for staff.')
        return data

    def create(self, validated_data):
        role = validated_data.pop('role')
        profile_data = {
            'admin_code': validated_data.pop('admin_code', ''),
            'specialization': validated_data.pop('specialization', ''),
            'license_number': validated_data.pop('license_number', ''),
            'hospital_name': validated_data.pop('hospital_name', ''),
            'date_of_birth': validated_data.pop('date_of_birth', None),
            'medical_history': validated_data.pop('medical_history', ''),
            'insurance_number': validated_data.pop('insurance_number', ''),
            'department': validated_data.pop('department', ''),
            'employee_id': validated_data.pop('employee_id', '')
        }
        
        user = User.objects.create_user(**validated_data, role=role)
        if role == 'admin':
            AdminProfile.objects.create(
                user=user, admin_code=profile_data.get('admin_code', ''))
        elif role == 'doctor':
            DoctorProfile.objects.create(
                user=user,
                specialization=profile_data.get('specialization', ''),
                license_number=profile_data.get('license_number', ''),
                hospital_name=profile_data.get('hospital_name', '')
            )
        elif role == 'patient':
            PatientProfile.objects.create(
                user=user,
                date_of_birth=profile_data.get('date_of_birth'),
                medical_history=profile_data.get('medical_history', ''),
                insurance_number=profile_data.get('insurance_number', '')
            )
        elif role == 'staff':
            StaffProfile.objects.create(
                user=user,
                department=profile_data.get('department', ''),
                employee_id=profile_data.get('employee_id', '')
            )
        return user

# Serializer for Login
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    # def validate(self, data):
    #     user = authenticate(username=data['username'], password=data['password'])
    #     if not user:
    #         raise serializers.ValidationError("Invalid credentials")
    #     return user

# Serializer for User Response
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.role == 'admin':
            representation['profile'] = AdminProfile.objects.filter(user=instance).values().first()
        elif instance.role == 'doctor':
            representation['profile'] = DoctorProfile.objects.filter(user=instance).values().first()
        elif instance.role == 'patient':
            representation['profile'] = PatientProfile.objects.filter(user=instance).values().first()
        elif instance.role == 'staff':
            representation['profile'] = StaffProfile.objects.filter(user=instance).values().first()
        

        
        return representation
    

class PatientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientProfile
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'


class StaffUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField()
    doctor = serializers.PrimaryKeyRelatedField(queryset=DoctorProfile.objects.all(), required=True)
    department = serializers.CharField(required=False, allow_blank=True)
    employee_id = serializers.CharField(required=False, allow_blank=True)
    role = serializers.CharField(default ='staff')
    permissions = serializers.PrimaryKeyRelatedField(queryset=Permission.objects.all(), many=True)
    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        role = validated_data.pop('role')
        permissions = validated_data.pop('permissions')

        profile_data = {
            'department': validated_data.pop('department', ''),
            'employee_id': validated_data.pop('employee_id', ''),
            'doctor' : validated_data.pop('doctor', ''),
        }
        
        user = User.objects.create_user(**validated_data, role="staff")
        if permissions:
            user.user_permissions.set(permissions)

        StaffProfile.objects.create(
            user=user,
            department=profile_data.get('department', ''),
            employee_id=profile_data.get('employee_id', ''),
            doctor = profile_data.get('doctor', '')
        )
        return user


from django.contrib.auth.models import Group, Permission

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']

class GroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']