from django.urls import path
from api.controllers.v1.health_controller import health_check
from api.controllers.v1.auth_controller import register, login, profile

urlpatterns = [
    path('v1/health-check/', health_check, name='health_check'),
    path('v1/auth/register/', register, name='register'),
    path('v1/auth/login/', login, name='login'),
    path('v1/auth/profile/', profile, name='profile'),
]
