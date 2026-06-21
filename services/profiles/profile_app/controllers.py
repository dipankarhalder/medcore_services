import json
import random
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from functools import wraps
import redis
from profile_app.models import UserProfile
from profile_app.kafka_producer import publish_event

signer = TimestampSigner()

# Connect to Redis container
r_cache = redis.Redis(host=os.getenv('REDIS_HOST', 'redis'), port=6379, db=0, decode_responses=True)

def token_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Authentication credentials were not provided.'}, status=401)
        
        try:
            token = auth_header.split(' ')[1]
            signed_val = signer.unsign(token, max_age=86400)
            if signed_val.startswith('patient:'):
                request.user_id = int(signed_val.split(':')[1])
                request.is_patient = True
            else:
                user_id, _ = signed_val.split(':')
                request.user_id = int(user_id)
                request.is_patient = False
        except (BadSignature, SignatureExpired, ValueError, IndexError):
            return JsonResponse({'error': 'Invalid or expired token.'}, status=401)
            
        return view_func(request, *args, **kwargs)
    return _wrapped

@csrf_exempt
@token_required
def get_profile(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed.'}, status=405)
        
    profile, created = UserProfile.objects.get_or_create(user_id=request.user_id)
    return JsonResponse({
        'profile': {
            'user_id': profile.user_id,
            'first_name': profile.first_name,
            'last_name': profile.last_name,
            'bio': profile.bio,
            'photo': profile.photo.url if profile.photo else None
        }
    })

@csrf_exempt
@token_required
def update_profile(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed.'}, status=405)
        
    try:
        data = json.loads(request.body)
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        bio = data.get('bio')
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)
        
    profile, _ = UserProfile.objects.get_or_create(user_id=request.user_id)
    if first_name is not None:
        profile.first_name = first_name
    if last_name is not None:
        profile.last_name = last_name
    if bio is not None:
        profile.bio = bio
    profile.save()
    
    return JsonResponse({
        'message': 'Profile updated successfully.',
        'profile': {
            'user_id': profile.user_id,
            'first_name': profile.first_name,
            'last_name': profile.last_name,
            'bio': profile.bio
        }
    })

@csrf_exempt
@token_required
def upload_photo(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed.'}, status=405)
        
    photo_file = request.FILES.get('photo')
    if not photo_file:
        return JsonResponse({'error': 'No image file provided.'}, status=400)
        
    profile, _ = UserProfile.objects.get_or_create(user_id=request.user_id)
    profile.photo = photo_file
    profile.save()
    
    return JsonResponse({
        'message': 'Profile photo uploaded.',
        'photo_url': profile.photo.url
    })

@csrf_exempt
@token_required
def send_otp(request):
    """
    Generate OTP, store in Redis with 5-minute expiry, and publish Kafka notification event.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed.'}, status=405)
        
    try:
        data = json.loads(request.body)
        channel = data.get('channel', 'email') # email or sms
        target = data.get('target') # email address or phone number
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)
        
    if not target:
        return JsonResponse({'error': 'Target recipient is required.'}, status=400)
        
    otp_code = str(random.randint(100000, 999999))
    
    # Save OTP to Redis with 5-minute (300 seconds) timeout
    try:
        r_cache.setex(f"otp:{request.user_id}", 300, otp_code)
    except Exception as e:
        return JsonResponse({'error': f"Redis error: {str(e)}"}, status=500)
        
    # Publish Kafka Event for notification delivery
    publish_event('notification_events', 'otp_generated', {
        'user_id': request.user_id,
        'otp_code': otp_code,
        'channel': channel,
        'target': target
    })
    
    return JsonResponse({'message': 'Verification code generated and sent.'})

@csrf_exempt
@token_required
def verify_otp(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed.'}, status=405)
        
    try:
        data = json.loads(request.body)
        otp_code = data.get('otp_code')
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)
        
    if not otp_code:
        return JsonResponse({'error': 'OTP code is required.'}, status=400)
        
    # Retrieve OTP from Redis
    cached_otp = r_cache.get(f"otp:{request.user_id}")
    if not cached_otp:
        return JsonResponse({'error': 'OTP expired or not requested.'}, status=400)
        
    if cached_otp == str(otp_code):
        r_cache.delete(f"otp:{request.user_id}") # Clear OTP once verified
        return JsonResponse({'message': 'OTP verified successfully.'})
    else:
        return JsonResponse({'error': 'Invalid OTP code.'}, status=400)

def health_check(request):
    return JsonResponse({'status': 'healthy', 'service': 'profiles'})
