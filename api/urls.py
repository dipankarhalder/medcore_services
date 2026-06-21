from django.urls import path
from api.controllers.v1.health_controller import health_check as v1_health_check
from api.controllers.v1.auth_controller import register as v1_register, login as v1_login, profile as v1_profile

urlpatterns = [
    path('v1/health-check/', v1_health_check, name='v1_health_check'),
    path('v1/auth/register/', v1_register, name='v1_register'),
    path('v1/auth/login/', v1_login, name='v1_login'),
    path('v1/auth/profile/', v1_profile, name='v1_profile'),
]
