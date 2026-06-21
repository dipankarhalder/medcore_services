from django.urls import path
from profile_app import controllers

urlpatterns = [
    path('profile/', controllers.get_profile, name='get_profile'),
    path('profile/update/', controllers.update_profile, name='update_profile'),
    path('profile/upload-photo/', controllers.upload_photo, name='upload_photo'),
    path('otp/send/', controllers.send_otp, name='send_otp'),
    path('otp/verify/', controllers.verify_otp, name='verify_otp'),
    path('health/', controllers.health_check, name='health_check'),
]
