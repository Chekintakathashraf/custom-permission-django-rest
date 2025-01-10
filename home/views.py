
from rest_framework.views import APIView
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token   
from .serializers import *
from rest_framework.response import Response
from rest_framework import viewsets


class AuthViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            user = authenticate(username = data['username'], 
                                password = data['password'])
            if user:
                token, _ = Token.objects.get_or_create(user = user)
                user_permissions = set()
                for perm in user.get_all_permissions():
                    user_permissions.add(perm)

                data = {
                    'token' : token.key,
                    'user': UserSerializer(user).data,
                    "user_permissions" : list(user_permissions)
                }
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response({
                    'message' : 'invalid password'
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class DoctorViewset(viewsets.ViewSet):

    authentication_class = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self , request):
        doctor = request.user.doctor if request.user.role == "doctor" else request.user.staff.doctor
        
        serializer =  UserSerializer(doctor.user)
        return Response(serializer.data)


    @action(detail=False, methods=['GET'])
    def get_appointments(self, request):
        doctor = None
        if request.user.role == "doctor":
            doctor = request.user.doctor
        else:
            doctor = request.user.staff.doctor
        serializer = AppointmentSerializer(Appointment.objects.filter(
         doctor = doctor
        ), many=True)
        return Response(serializer.data)
    

    @action(detail=False, methods=['GET'])
    def get_patients(self, request):
        serializer = PatientProfileSerializer(PatientProfile.objects.all())
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def get_staff_permissions(self, request):
        group = Group.objects.filter(name = 'staff')
        if not group:
            return Response({"detail": "Group 'staff' not found."}, status=404)
        serializer = GroupSerializer(group[0])

        return Response(serializer.data)


    @action(detail=False, methods=['POST'])
    def update_staff(self, request):
        data = request.data
        doctor = request.user.doctor if request.user.role == "doctor" else request.user.staff.doctor

        data['doctor'] = doctor.id
        staff_id = data.get('staff_id')
        serializer = StaffUserSerializer(
            User.objects.get(id = staff_id),
            data = data, partial = True)
        if serializer.is_valid():
            user = serializer.save()
            return Response(StaffUserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    @action(detail=False, methods=['POST'])
    def create_staff(self, request):
        data = request.data
        doctor = request.user.doctor if request.user.role == "doctor" else request.user.staff.doctor

        data['doctor'] = doctor.id
        serializer = StaffUserSerializer(data = data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)