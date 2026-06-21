from django.urls import path, include

urlpatterns = [
    path('api/v1/auth/', include('auth_app.urls')),
]
