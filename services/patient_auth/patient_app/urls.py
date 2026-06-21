from django.urls import path
from patient_app import controllers

urlpatterns = [
    path('register/', controllers.register, name='register'),
    path('login/', controllers.login, name='login'),
    path('health/', controllers.health_check, name='health_check'),
]
