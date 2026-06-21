import time
from django.db import connection
from django.http import JsonResponse

def health_check(request):
    """
    Health Check API to verify application status and database connectivity.
    """
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {
            "database": "unhealthy"
        }
    }
    
    try:
        connection.ensure_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["services"]["database"] = f"unhealthy: {str(e)}"
        
    status_code = 200 if health_status["status"] == "healthy" else 500
    return JsonResponse(health_status, status=status_code)
