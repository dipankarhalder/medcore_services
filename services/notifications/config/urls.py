from django.urls import path
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'healthy', 'service': 'notifications'})

urlpatterns = [
    path('api/v1/notifications/health/', health_check, name='health_check'),
]
