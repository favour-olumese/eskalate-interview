import cloudinary.uploader
from django.core.mail import send_mail
from django.conf import settings
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from rest_framework.reverse import reverse

def upload_to_cloudinary(file_obj):
    """
    Uploads a file to Cloudinary and returns the secure URL.
    """
    try:
        upload_result = cloudinary.uploader.upload(file_obj)
        return upload_result['secure_url']
    except Exception as e:
        # Handle exceptions, maybe log them
        raise e

def send_verification_email(user, request):
    """
    Generates a verification token and sends it to the user's email.
    """
    signer = TimestampSigner()
    token = signer.sign(str(user.id))
    verification_link = request.build_absolute_uri(
        reverse('verify-email') + f'?token={token}'
    )

    subject = 'Verify Your Email for Job Portal'
    message = (
        f'Hi {user.name},\n\n'
        f'Please click the link below to verify your email address:\n'
        f'{verification_link}\n\n'
        'This link will expire in 1 hour.\n\n'
        'Thanks,\nThe Job Portal Team'
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])