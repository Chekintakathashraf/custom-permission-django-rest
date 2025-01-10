from rest_framework import permissions

class IsDoctor(permissions.BasePermission):
    """
    Custom permission to allow only doctors to view their appointments.
    """
    def has_permission(self, request, view):

        return request.user.role == 'doctor' or  request.user.role == 'staff'
    
    def has_object_permission(self, request, view, obj):
        print(request,view, obj)

        return True