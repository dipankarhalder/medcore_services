import json
import time
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from functools import wraps
from auth_app.models import User, UserSession
from auth_app.kafka_producer import publish_event

signer = TimestampSigner()

def token_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Authentication credentials were not provided.'}, status=401)
        
        try:
            token = auth_header.split(' ')[1]
            signed_val = signer.unsign(token, max_age=86400)
            user_id, session_key = signed_val.split(':')
            user = User.objects.get(id=int(user_id))
            session = UserSession.objects.get(session_key=session_key, is_active=True)
            request.user = user
            request.session_key = session_key
        except (BadSignature, SignatureExpired, ValueError, IndexError, User.DoesNotExist, UserSession.DoesNotExist):
            return JsonResponse({'error': 'Invalid or expired session.'}, status=401)
            
        return view_func(request, *args, **kwargs)
    return _wrapped

@csrf_exempt
def register(request):
    """
    User Registration / Creation.
    First time registration bootstraps the system as super_admin.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed.'}, status=405)
        
    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        phone_number = data.get('phone_number')
        role = data.get('role', 'staff')
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)

    db_empty = not User.objects.exists()
    
    if db_empty:
        # First user is super admin and auto-verified
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                phone_number=phone_number,
                role='super_admin',
                is_email_verified=True,
                is_phone_verified=True
            )
            # Create session
            session_key = str(uuid.uuid4())
            UserSession.objects.create(
                user=user,
                session_key=session_key,
                device_name=request.META.get('HTTP_USER_AGENT', 'Unknown'),
                ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1')
            )
            token = signer.sign(f"{user.id}:{session_key}")
            
            # Publish Kafka Welcome Event
            publish_event('admin_auth_events', 'user_registered', {
                'username': user.username,
                'email': user.email,
                'role': user.role
            })
            
            return JsonResponse({
                'token': token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role
                }
            }, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    # Non-bootstrap flow: Requires admin authentication
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'error': 'Only Super Admins or Admins can register new users.'}, status=401)
        
    try:
        token = auth_header.split(' ')[1]
        signed_val = signer.unsign(token, max_age=86400)
        creator_id, _ = signed_val.split(':')
        creator = User.objects.get(id=int(creator_id))
    except Exception:
        return JsonResponse({'error': 'Invalid authorization token.'}, status=401)
        
    if creator.role not in ['super_admin', 'admin']:
        return JsonResponse({'error': 'Permission denied. Only Super Admins or Admins can register new users.'}, status=403)
        
    if role == 'super_admin' and creator.role != 'super_admin':
        return JsonResponse({'error': 'Admins cannot create Super Admin users.'}, status=403)
        
    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': 'Username is already taken.'}, status=400)
        
    if User.objects.filter(email=email).exists():
        return JsonResponse({'error': 'Email is already registered.'}, status=400)
        
    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            phone_number=phone_number,
            role=role
        )
        publish_event('admin_auth_events', 'user_registered', {
            'username': user.username,
            'email': user.email,
            'role': user.role
        })
        return JsonResponse({
            'message': 'User registered successfully.',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
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
            return JsonResponse({'error': 'Account is disabled.'}, status=403)
            
        # Device limit check (super_admin and admin only allow 4 active devices)
        if user.role in ['super_admin', 'admin']:
            active_sessions = UserSession.objects.filter(user=user, is_active=True).count()
            if active_sessions >= 4:
                return JsonResponse({'error': 'Device session limit exceeded. Maximum 4 active devices allowed.'}, status=400)
                
        # Register new session
        session_key = str(uuid.uuid4())
        UserSession.objects.create(
            user=user,
            session_key=session_key,
            device_name=request.META.get('HTTP_USER_AGENT', 'Unknown'),
            ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1')
        )
        token = signer.sign(f"{user.id}:{session_key}")
        
        return JsonResponse({
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        })
    else:
        return JsonResponse({'error': 'Invalid credentials.'}, status=400)

@csrf_exempt
@token_required
def logout(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed.'}, status=405)
        
    UserSession.objects.filter(session_key=request.session_key).update(is_active=False)
    return JsonResponse({'message': 'Logged out successfully.'})

@csrf_exempt
@token_required
def list_sessions(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed.'}, status=405)
        
    sessions = UserSession.objects.filter(user=request.user, is_active=True).values(
        'session_key', 'device_name', 'ip_address', 'created_at', 'last_activity'
    )
    return JsonResponse({'sessions': list(sessions)})

@csrf_exempt
@token_required
def logout_device(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed.'}, status=405)
        
    try:
        data = json.loads(request.body)
        target_session = data.get('session_key')
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)
        
    UserSession.objects.filter(user=request.user, session_key=target_session).update(is_active=False)
    return JsonResponse({'message': 'Device logged out.'})

@csrf_exempt
@token_required
def logout_all_devices(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed.'}, status=405)
        
    UserSession.objects.filter(user=request.user).update(is_active=False)
    return JsonResponse({'message': 'All devices logged out.'})

@csrf_exempt
def forgot_password(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed.'}, status=405)
    return JsonResponse({'message': 'Reset link dispatched (Stub).'})

def health_check(request):
    return JsonResponse({'status': 'healthy', 'service': 'admin_auth'})
