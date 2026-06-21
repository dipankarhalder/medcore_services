import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.signing import TimestampSigner
from patient_app.models import Patient

signer = TimestampSigner()

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

    if Patient.objects.filter(username=username).exists():
        return JsonResponse({'error': 'Username is already taken.'}, status=400)

    if Patient.objects.filter(email=email).exists():
        return JsonResponse({'error': 'Email is already registered.'}, status=400)

    try:
        patient = Patient(username=username, email=email, phone_number=phone_number)
        patient.set_password(password)
        patient.save()
        
        token = signer.sign(f"patient:{patient.id}")
        return JsonResponse({
            'token': token,
            'patient': {
                'id': patient.id,
                'username': patient.username,
                'email': patient.email
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
        email = data.get('email')
        password = data.get('password')
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)

    if not email or not password:
        return JsonResponse({'error': 'Email and password are required.'}, status=400)

    try:
        patient = Patient.objects.get(email=email)
    except Patient.DoesNotExist:
        return JsonResponse({'error': 'Invalid credentials.'}, status=400)

    if patient.check_password(password):
        token = signer.sign(f"patient:{patient.id}")
        return JsonResponse({
            'token': token,
            'patient': {
                'id': patient.id,
                'username': patient.username,
                'email': patient.email
            }
        })
    else:
        return JsonResponse({'error': 'Invalid credentials.'}, status=400)

def health_check(request):
    return JsonResponse({'status': 'healthy', 'service': 'patient_auth'})
