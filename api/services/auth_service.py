from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from api.models import User

signer = TimestampSigner()

def generate_token(user_id):
    """
    Generate a signed timestamp token for the user_id.
    """
    return signer.sign(str(user_id))

def verify_token(token, max_age=86400):
    """
    Verify the token signature and age. Returns the User instance if valid, else None.
    """
    try:
        user_id = signer.unsign(token, max_age=max_age)
        return User.objects.get(id=int(user_id))
    except (BadSignature, SignatureExpired, ValueError, User.DoesNotExist):
        return None
