from django.urls import path, include

urlpatterns = [
    path('api/v1/patients/', include('patient_app.urls')),
]
