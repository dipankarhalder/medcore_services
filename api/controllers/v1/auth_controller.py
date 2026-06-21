import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from api.models import User
from api.services.auth_service import generate_token
from api.decorators import token_required

@csrf_exempt
def register(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed.'}, status=405)
    
    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        phone_number = data.get('phone_number')
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)
        
    if not username or not email or not password:
        return JsonResponse({'error': 'Username, email, and password are required.'}, status=400)
        
    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': 'Username is already taken.'}, status=400)
        
    if User.objects.filter(email=email).exists():
        return JsonResponse({'error': 'Email is already registered.'}, status=400)
        
    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            phone_number=phone_number
        )
        token = generate_token(user.id)
        return JsonResponse({
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'phone_number': user.phone_number
            }
        }, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def login(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed.'}, status=405)
        
    try:
        data = json.loads(request.body)
        username_or_email = data.get('username') or data.get('email')
        password = data.get('password')
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)
        
    if not username_or_email or not password:
        return JsonResponse({'error': 'Username/email and password are required.'}, status=400)
        
    user = None
    if '@' in username_or_email:
        try:
            user = User.objects.get(email=username_or_email)
        except User.DoesNotExist:
            pass
    
    if not user:
        try:
            user = User.objects.get(username=username_or_email)
        except User.DoesNotExist:
            pass
            
    if user and user.check_password(password):
        if not user.is_active:
            return JsonResponse({'error': 'User account is disabled.'}, status=400)
            
        token = generate_token(user.id)
        return JsonResponse({
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'phone_number': user.phone_number
            }
        })
    else:
        return JsonResponse({'error': 'Invalid credentials.'}, status=400)

@csrf_exempt
@token_required
def profile(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed.'}, status=405)
        
    return JsonResponse({
        'user': {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'phone_number': request.user.phone_number,
            'date_joined': request.user.date_joined.isoformat()
        }
    })
