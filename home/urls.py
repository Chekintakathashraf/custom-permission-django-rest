from django.contrib import admin
from django.urls import path
from home import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from home.views import AuthViewSet,DoctorViewset

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'doctor', DoctorViewset, basename='doctor')

urlpatterns = [

    path('', include(router.urls)),
]