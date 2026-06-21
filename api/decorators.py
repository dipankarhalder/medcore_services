from django.http import JsonResponse
from functools import wraps
from api.services.auth_service import verify_token

def token_required(view_func):
    """
    Decorator to protect views. Resolves Bearer tokens from the Authorization header.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Authentication credentials were not provided.'}, status=401)
        
        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            return JsonResponse({'error': 'Invalid authorization header format.'}, status=401)
            
        user = verify_token(token)
        if not user:
            return JsonResponse({'error': 'Invalid or expired token.'}, status=401)
        
        request.user = user
        return view_func(request, *args, **kwargs)
    return _wrapped_view
