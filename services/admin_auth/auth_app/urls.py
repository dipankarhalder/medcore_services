from django.urls import path
from auth_app import controllers

urlpatterns = [
    path('register/', controllers.register, name='register'),
    path('login/', controllers.login, name='login'),
    path('logout/', controllers.logout, name='logout'),
    path('sessions/', controllers.list_sessions, name='list_sessions'),
    path('sessions/logout-device/', controllers.logout_device, name='logout_device'),
    path('sessions/logout-all/', controllers.logout_all_devices, name='logout_all_devices'),
    path('forgot-password/', controllers.forgot_password, name='forgot_password'),
    path('health/', controllers.health_check, name='health_check'),
]
